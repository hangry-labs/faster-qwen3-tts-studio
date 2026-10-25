import { test } from 'node:test'
import assert from 'node:assert/strict'
import { generateRequestId } from '../../src/faster_qwen3_tts/standalone_ui/static/request-id.js'

test('secure origins retain native UUID request correlation', () => {
  assert.equal(generateRequestId({ randomUUID: () => 'native-request-id' }), 'native-request-id')
})

test('HTTP LAN origins generate valid distinct correlation IDs without randomUUID', () => {
  let count = 0
  const source = { getRandomValues: bytes => { bytes.fill(++count); return bytes } }
  const first = generateRequestId(source), second = generateRequestId(source)
  assert.match(first, /^[a-f0-9]{32}$/)
  assert.notEqual(first, second)
})
