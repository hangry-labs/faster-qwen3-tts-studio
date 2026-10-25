// Adapted from VoxCPMTTS with Qwen-specific storage/bootstrap names; see NOTICE.
const bootstrap = globalThis.window?.__QWEN3TTS_UI__ || {
  locale: 'en',
  defaultLocale: 'en',
  locales: [{ code: 'en', name: 'English', path: '/en', direction: 'ltr', browserLanguage: 'en-US' }],
  storageKey: 'qwen3tts-ui-locale-v1',
}

let messages = bootstrap.messages || {}
const renderedMessages = new Map()
let localeRequest = 0

const LANGUAGE_CODES = {
  arabic: 'ar', burmese: 'my', chinese: 'zh', danish: 'da', dutch: 'nl', english: 'en',
  finnish: 'fi', french: 'fr', german: 'de', greek: 'el', hebrew: 'he', hindi: 'hi',
  indonesian: 'id', italian: 'it', japanese: 'ja', khmer: 'km', korean: 'ko', lao: 'lo',
  malay: 'ms', norwegian: 'no', polish: 'pl', portuguese: 'pt', russian: 'ru', spanish: 'es',
  swahili: 'sw', swedish: 'sv', tagalog: 'tl', thai: 'th', turkish: 'tr', vietnamese: 'vi',
}

async function loadCatalog(locale) {
  const response = await fetch(`/static/locales/${encodeURIComponent(locale)}.json`)
  if (!response.ok) throw new Error(`Unable to load UI locale ${locale}.`)
  return response.json()
}

function interpolate(template, variables) {
  return template.replace(/\{([a-zA-Z0-9_]+)\}/g, (match, name) => (
    Object.hasOwn(variables, name) ? String(variables[name]) : match
  ))
}

export function t(key, variables = {}, fallback = key) {
  const value = messages[key]
  return interpolate(typeof value === 'string' ? value : fallback, variables)
}

// Source-keyed messages complement the shared semantic catalog. Tagged templates
// keep interpolated user content separate from translated interface text.
export function msg(source, ...values) {
  if (typeof source === 'string') {
    const result = t(`text:${source}`, {}, source)
    renderedMessages.set(result, { source, values })
    return result
  }
  const template = source.reduce((text, part, index) => text + (index ? `{${index - 1}}` : '') + part, '')
  const translated = messages[`text:${template}`] || template
  const result = translated.replace(/\{(\d+)\}/g, (match, index) => index < values.length ? String(values[index]) : match)
  // Only fixed messages are retained. Never keep interpolated user content in
  // this registry; callers re-render dynamic status from current state instead.
  return result
}

export function retranslate(value) {
  const original = renderedMessages.get(value)
  return original ? msg(original.source, ...original.values) : t(`text:${value}`, {}, value)
}

export function browserLanguage() {
  return bootstrap.locales.find((item) => item.code === bootstrap.locale)?.browserLanguage || bootstrap.locale
}

export function languageLabel(language) {
  if (!language) return ''
  if (String(language).toLowerCase() === 'auto') return msg('Automatic')
  const key = String(language).toLowerCase().replaceAll(' ', '_')
  try {
    return new Intl.DisplayNames([browserLanguage()], { type: 'language' }).of(LANGUAGE_CODES[key]) || language
  } catch {
    return t(`languages.${key}`, {}, language)
  }
}

export function applyTranslations(root = document) {
  root.querySelectorAll('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n, {}, node.textContent)
  })
  for (const attribute of ['title', 'aria-label', 'placeholder', 'alt']) {
    const dataName = `i18n${attribute.split('-').map((part) => part[0].toUpperCase() + part.slice(1)).join('')}`
    root.querySelectorAll(`[data-i18n-${attribute}]`).forEach((node) => {
      node.setAttribute(attribute, t(node.dataset[dataName], {}, node.getAttribute(attribute) || ''))
    })
  }
  root.querySelectorAll('[data-i18n-value]').forEach((node) => {
    node.value = t(node.dataset.i18nValue, {}, node.value || '')
  })
}

function populateLocalePicker() {
  const picker = document.querySelector('#ui-locale')
  if (!picker) return
  picker.disabled = true
  picker.replaceChildren(...bootstrap.locales.map((locale) => {
    const option = document.createElement('option')
    option.value = locale.code
    option.textContent = locale.name
    option.selected = locale.code === bootstrap.locale
    return option
  }))
  picker.addEventListener('change', () => {
    const locale = bootstrap.locales.find((item) => item.code === picker.value)
    if (!locale) return
    // Change only interface messages. Navigating/reloading here would discard
    // unsaved dialogue, reference recordings, takes and generated browser audio.
    picker.disabled = true
    setLocale(locale.code).catch(() => {
      window.dispatchEvent(new CustomEvent('ui-locale-error', { detail: msg('Unable to change interface language. Check the connection and try again.') }))
    }).finally(() => { picker.value = bootstrap.locale; picker.disabled = false })
  })
}

export async function setLocale(locale) {
  const entry = bootstrap.locales.find(item => item.code === locale)
  if (!entry) return
  const revision = ++localeRequest
  const [english, translated] = await Promise.all([loadCatalog(bootstrap.defaultLocale),
    locale === bootstrap.defaultLocale ? {} : loadCatalog(locale)])
  if (revision !== localeRequest) return
  messages = { ...english, ...Object.fromEntries(Object.entries(translated).filter(([, value]) => typeof value === 'string' && value.trim())) }
  bootstrap.locale = locale
  document.documentElement.lang = locale
  document.documentElement.dir = entry.direction || 'ltr'
  try { localStorage.setItem(bootstrap.storageKey, locale) } catch {}
  history.replaceState(null, '', entry.path + location.search + location.hash)
  const picker = document.querySelector('#ui-locale')
  if (picker) picker.value = locale
  // Dynamic components subscribe to this event. Existing user inputs are never
  // translated or persisted as a side effect of choosing an interface language.
  applyTranslations()
  document.title = t('app.title', {}, document.title)
  window.dispatchEvent(new CustomEvent('ui-locale-changed'))
}

export async function initializeI18n() {
  if (!Object.keys(messages).length) {
    try {
      messages = await loadCatalog(bootstrap.locale)
    } catch (error) {
      console.error(error)
    }
  }

  document.documentElement.lang = bootstrap.locale
  document.documentElement.dir = bootstrap.locales.find((item) => item.code === bootstrap.locale)?.direction || 'ltr'
  document.title = t('app.title', {}, document.title)
  try { localStorage.setItem(bootstrap.storageKey, bootstrap.locale) } catch {}
  applyTranslations()
  populateLocalePicker()
}
