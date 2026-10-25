import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { speechSample } from '../../src/faster_qwen3_tts/standalone_ui/static/speech-samples.js'

const locales = ['en', 'nb', 'pl', 'ja', 'zh', 'es']
const catalogs = Object.fromEntries(await Promise.all(locales.map(async code => [code,
  JSON.parse(await readFile(new URL(`../../src/faster_qwen3_tts/standalone_ui/static/locales/${code}.json`, import.meta.url), 'utf8'))])))
let instance = 0
async function setup(fetchOverride) {
  const events = [], stored = new Map(), paths = [], picker = { value: 'en' }
  globalThis.window = { __QWEN3TTS_UI__: { locale: 'en', defaultLocale: 'en', storageKey: 'locale',
    messages: catalogs.en, locales: locales.map(code => ({ code, path: '/' + code, direction: 'ltr' })) },
    dispatchEvent: event => events.push(event.type) }
  globalThis.document = { documentElement: {}, title: '', querySelector: () => picker, querySelectorAll: () => [] }
  globalThis.location = { search: '?test=1', hash: '#clone' }
  globalThis.history = { replaceState: (state, title, path) => paths.push(path) }
  globalThis.localStorage = { setItem: (key, value) => stored.set(key, value) }
  globalThis.fetch = fetchOverride || (async url => ({ ok: true, json: async () => catalogs[url.match(/(\w+)\.json$/)[1]] }))
  const i18n = await import(`../../src/faster_qwen3_tts/standalone_ui/static/i18n.js?test=${instance++}`)
  return { ...i18n, events, stored, paths, picker }
}

test('all six catalogs keep the same keys and interpolation variables', () => {
  const variables = value => [...value.matchAll(/\{([a-zA-Z0-9_]+)\}/g)].map(match => match[1]).sort()
  for (const locale of locales) {
    assert.deepEqual(Object.keys(catalogs[locale]).sort(), Object.keys(catalogs.en).sort(), locale)
    for (const [key, value] of Object.entries(catalogs[locale])) {
      assert.ok(typeof value === 'string' && value.trim(), `${locale}: ${key}`)
      assert.deepEqual(variables(value), variables(catalogs.en[key]), `${locale}: ${key}`)
      assert.ok(!value.includes('\ufffd'), `${locale}: ${key}`)
    }
  }
})

test('changing locale updates interface, preference and URL without navigation', async () => {
  const app = await setup()
  const english = app.msg('Generate speech')
  await app.setLocale('ja')
  assert.equal(app.msg('Generate speech'), '音声を生成')
  assert.equal(app.retranslate(english), '音声を生成')
  assert.equal(document.documentElement.lang, 'ja')
  assert.deepEqual(app.paths, ['/ja?test=1#clone'])
  assert.equal(app.stored.get('locale'), 'ja')
  assert.deepEqual(app.events, ['ui-locale-changed'])
})

test('interpolation preserves user content with braces and markup literally', async () => {
  const app = await setup()
  await app.setLocale('es')
  const name = '<Captain> ${voice} {0} & $&'
  assert.equal(app.msg`Preview ${name}`, `Escuchar ${name}`)
  assert.equal(app.msg('Untranslated control'), 'Untranslated control')
})

test('a missing translation falls back to English and failed loading is atomic', async () => {
  let fail = false
  const app = await setup(async url => ({ ok: !fail,
    json: async () => url.endsWith('/en.json') ? catalogs.en : { 'text:Generate speech': '' } }))
  await app.setLocale('pl')
  assert.equal(app.msg('Generate speech'), 'Generate speech')
  fail = true
  await assert.rejects(app.setLocale('ja'))
  assert.equal(document.documentElement.lang, 'pl')
  assert.equal(app.stored.get('locale'), 'pl')
  await app.setLocale('unsupported')
  assert.equal(document.documentElement.lang, 'pl')
})

test('a late catalog response cannot override a newer locale choice', async () => {
  let release
  const held = new Promise(resolve => { release = resolve })
  const app = await setup(async url => {
    if (url.endsWith('/ja.json')) await held
    return { ok: true, json: async () => catalogs[url.match(/(\w+)\.json$/)[1]] }
  })
  const pending = app.setLocale('ja')
  await app.setLocale('pl')
  release(); await pending
  assert.equal(document.documentElement.lang, 'pl')
  assert.equal(app.picker.value, 'pl')
})

test('speech examples follow Qwen language choices and never add unsupported speech languages', () => {
  assert.match(speechSample('Japanese'), /おはよう/)
  assert.match(speechSample('Spanish'), /Buenos días/)
  assert.equal(speechSample('Auto'), speechSample('English'))
  assert.equal(speechSample('Polish'), speechSample('English'))
})
