import { test } from 'node:test'
import assert from 'node:assert/strict'
import { voiceRecipe, canReplaceVoice } from '../../src/faster_qwen3_tts/standalone_ui/static/voice-library.js'

test('saved recipe locks the actual generated seed and snapshots settings without rewriting the request', () => {
  const context = { recipe: { workflow: 'design', settings: { instruct: 'Warm', seed: null } }, metrics: { seed: 4294967295 } }
  const finishing = { options: { room: 3 }, processedOptions: { room: 3 } }
  const saved = voiceRecipe(context, finishing, 'processed')
  assert.equal(saved.settings.seed, 4294967295)
  assert.equal(saved.settings.randomize_seed, false)
  assert.equal(saved.selected_version, 'processed')
  context.recipe.settings.instruct = 'Changed after generation'
  finishing.options.room = 8
  assert.equal(saved.settings.instruct, 'Warm')
  assert.equal(saved.finishing.options.room, 3)
})

test('restored or previous recordings cannot qualify as fresh replacements', () => {
  const refinement = { startedAt: 100 }
  for (const generatedAt of [undefined, null, NaN, 99, 100]) assert.equal(canReplaceVoice({ generatedAt }, refinement), false)
  assert.equal(canReplaceVoice({ generatedAt: 101 }, refinement), true)
  assert.equal(canReplaceVoice({ generatedAt: 101 }, null), false)
})
