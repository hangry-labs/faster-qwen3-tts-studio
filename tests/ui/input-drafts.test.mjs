import { test } from 'node:test'
import assert from 'node:assert/strict'
import { InputDrafts } from '../../src/faster_qwen3_tts/standalone_ui/static/input-drafts.js'

function fixture() {
  let magic = '<speak>Magic draft</speak>', imports = 0
  const drafts = new InputDrafts({ text: 'Plain example.', ssml: '<speak>SSML example.</speak>',
    serializeMagic: () => magic,
    loadMagic: source => { if (!source.startsWith('<speak>')) throw new Error('Invalid markup'); magic = source; imports++ },
  })
  return { drafts, magic: () => magic, imports: () => imports }
}

test('all sixteen input-mode transitions preserve independent drafts', () => {
  for (const from of ['magic', 'text', 'ssml', 'ssml-h']) {
    for (const to of ['magic', 'text', 'ssml', 'ssml-h']) {
      const { drafts } = fixture()
      let value = drafts.switchTo(from, '')
      value = drafts.switchTo(to, value)
      if (to === 'text') assert.equal(value, 'Plain example.', `${from} -> ${to}`)
      if (to === 'ssml') assert.equal(value, '<speak>SSML example.</speak>', `${from} -> ${to}`)
    }
  }
})

test('long mixed sequences cannot put markup into the plain-text draft', () => {
  const { drafts } = fixture()
  let value = drafts.switchTo('text', '')
  value = 'My edited text <literally written>.'
  for (const mode of ['ssml', 'ssml-h', 'text', 'magic', 'ssml-h', 'ssml', 'magic', 'text']) value = drafts.switchTo(mode, value)
  assert.equal(value, 'My edited text <literally written>.')
})

test('failed SSML-H import is atomic and a corrected draft can be imported', () => {
  const { drafts, magic, imports } = fixture()
  drafts.switchTo('ssml-h', '')
  assert.throws(() => drafts.switchTo('magic', 'broken'), /Invalid markup/)
  assert.equal(drafts.mode, 'ssml-h')
  assert.equal(drafts.drafts['ssml-h'], 'broken')
  assert.equal(magic(), '<speak>Magic draft</speak>')
  drafts.switchTo('magic', '<speak>Fixed.</speak>')
  assert.equal(magic(), '<speak>Fixed.</speak>')
  assert.equal(imports(), 1)
})

test('unchanged Magic round trip does not reload or discard generated takes', () => {
  const { drafts, imports } = fixture()
  const exported = drafts.switchTo('ssml-h', '')
  drafts.switchTo('magic', exported)
  assert.equal(imports(), 0)
})

test('programmatic script loading does not import the previous raw draft', () => {
  const { drafts, imports } = fixture()
  drafts.switchTo('ssml-h', '')
  drafts.switchTo('magic', 'broken', { syncSsmlH: false })
  assert.equal(imports(), 0)
  assert.equal(drafts.mode, 'magic')
})
