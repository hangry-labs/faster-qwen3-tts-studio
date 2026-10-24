import { test } from 'node:test'
import assert from 'node:assert/strict'
import { AudioEditor } from '../../src/faster_qwen3_tts/standalone_ui/static/audio-editor.js'

// Exercise the real asynchronous load/clear methods with a deferred media
// backend, so completion order is deterministic without a browser decoder.
function fixture() {
  const pending = [], changes = []
  const editor = Object.create(AudioEditor.prototype)
  Object.assign(editor, {
    disableTrim() {}, setPlayIcon() {},
    setAudioActionsEnabled(value) { this.enabled = value },
    wave: { pause() {}, empty() {}, setTime() {}, load() { return new Promise((resolve, reject) => pending.push({ resolve, reject })) } },
    container: { classList: { add() {}, remove() {} } },
    filenameElement: {}, currentElement: {}, durationElement: {}, emptyElement: {},
    labels: { noAudio: 'No audio' }, onChange: file => changes.push(file),
  })
  return { editor, pending, changes }
}

test('a superseded failed decoder cannot clear a newer successful recording', async () => {
  const { editor, pending, changes } = fixture()
  const old = editor.load(new File(['old'], 'old.wav'))
  const currentFile = new File(['new'], 'new.wav')
  const current = editor.load(currentFile)
  pending[1].resolve(); await current
  pending[0].reject(new DOMException('Superseded', 'AbortError')); await old
  assert.equal(editor.currentFile(), currentFile)
  assert.equal(editor.enabled, true)
  assert.deepEqual(changes, [currentFile])
  editor.clear()
})

test('a superseded successful decoder cannot reset the current recording', async () => {
  const { editor, pending, changes } = fixture()
  const old = editor.load(new File(['old'], 'old.wav'))
  const currentFile = new File(['new'], 'new.wav')
  const current = editor.load(currentFile)
  pending[0].resolve(); await old
  assert.equal(editor.enabled, false)
  assert.deepEqual(changes, [])
  pending[1].resolve(); await current
  assert.deepEqual(changes, [currentFile])
  editor.clear()
})

test('clearing a pending load keeps playback disabled after it completes', async () => {
  const { editor, pending, changes } = fixture()
  const loading = editor.load(new File(['sample'], 'sample.wav'))
  editor.clear()
  pending[0].resolve(); await loading
  assert.equal(editor.currentFile(), null)
  assert.equal(editor.enabled, false)
  assert.deepEqual(changes, [null])
})

test('a current decoder failure clears invalid audio and reports the error', async () => {
  const { editor, pending } = fixture()
  const loading = editor.load(new File(['invalid'], 'invalid.wav'))
  pending[0].reject(new Error('Decode failed'))
  await assert.rejects(loading, /Decode failed/)
  assert.equal(editor.currentFile(), null)
  assert.equal(editor.enabled, false)
})
