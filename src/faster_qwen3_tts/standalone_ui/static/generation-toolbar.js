import { msg } from './i18n.js'
// Shared VoxCPMTTS menu behavior, mapped to Qwen's actual sampling controls.
const CONTROL_IDS = {
  temperature: 'temperature', topK: 'top-k', repetition: 'repetition',
  context: 'decoder-context', chunk: 'chunk-size', tokens: 'max-tokens', feed: 'text-feed', speed: 'speech-speed',
  seed: 'seed',
  randomize: 'random-seed',
  protect: 'protect-long',
  loudness: 'normalize-loudness',
}

export class GenerationToolbar {
  constructor(root, { randomLabel = msg('Randomize') } = {}) {
    this.root = root
    this.randomLabel = randomLabel
    this.openName = null
    this.menus = new Map([...root.querySelectorAll('[data-generation-menu]')].map((wrapper) => [
      wrapper.dataset.generationMenu,
      {
        wrapper,
        trigger: wrapper.querySelector('[data-generation-menu-trigger]'),
        panel: wrapper.querySelector('[data-generation-menu-panel]'),
      },
    ]))
    this.bind()
    this.sync()
  }

  bind() {
    this.root.querySelectorAll('[data-generation-reset]').forEach(button => button.addEventListener('click', () => {
      document.getElementById('reset-controls').click()
      this.sync()
    }))
    for (const [name, menu] of this.menus) {
      menu.trigger.addEventListener('click', () => {
        if (this.openName === name) this.close()
        else this.open(name)
      })
    }

    this.root.querySelectorAll('[data-generation-proxy]').forEach((proxy) => {
      const name = proxy.dataset.generationProxy
      const source = document.getElementById(CONTROL_IDS[name])
      if (!source) return
      const eventName = proxy.type === 'checkbox' || proxy.tagName === 'SELECT' ? 'change' : 'input'
      proxy.addEventListener(eventName, () => {
        if (proxy.type === 'checkbox') source.checked = proxy.checked
        else {
          source.value = proxy.value
          const pairedRange = document.getElementById(`${CONTROL_IDS[name]}-slider`)
          if (pairedRange) pairedRange.value = proxy.value
        }
        source.dispatchEvent(new Event(eventName, { bubbles: true }))
        this.sync()
      })
      source.addEventListener(eventName, () => this.sync())
    })

    document.addEventListener('pointerdown', (event) => {
      const menu = this.menus.get(this.openName)
      if (menu && !menu.wrapper.contains(event.target)) this.close()
    })
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !this.openName) return
      const trigger = this.menus.get(this.openName)?.trigger
      this.close()
      trigger?.focus()
    })
    window.addEventListener('resize', () => this.close())
  }

  open(name) {
    const menu = this.menus.get(name)
    if (!menu) return
    this.close({ except: name })
    this.openName = name
    menu.panel.hidden = false
    menu.trigger.classList.add('open')
    menu.trigger.setAttribute('aria-expanded', 'true')
    this.anchor(menu.panel, menu.trigger)
  }

  close({ except = null } = {}) {
    for (const [name, menu] of this.menus) {
      if (name === except) continue
      menu.panel.hidden = true
      menu.trigger.classList.remove('open')
      menu.trigger.setAttribute('aria-expanded', 'false')
      menu.panel.style.removeProperty('left')
      menu.panel.style.removeProperty('top')
    }
    if (!except || this.openName !== except) this.openName = except
  }

  anchor(panel, trigger) {
    const rect = trigger.getBoundingClientRect()
    panel.style.left = '8px'
    panel.style.top = '8px'
    const width = panel.offsetWidth
    const height = panel.offsetHeight
    const left = Math.max(8, Math.min(rect.left, window.innerWidth - width - 8))
    const top = rect.bottom + 6 + height <= window.innerHeight
      ? rect.bottom + 6
      : Math.max(8, rect.top - height - 6)
    panel.style.left = `${left}px`
    panel.style.top = `${top}px`
  }

  sync() {
    for (const [name, id] of Object.entries(CONTROL_IDS)) {
      const source = document.getElementById(id)
      if (!source) continue
      this.root.querySelectorAll(`[data-generation-proxy="${name}"]`).forEach((proxy) => {
        if (proxy.type === 'checkbox') proxy.checked = source.checked
        else proxy.value = source.value
      })
    }

    const temperature = document.getElementById(CONTROL_IDS.temperature)?.value || '0.9'
    const topK = document.getElementById(CONTROL_IDS.topK)?.value || '50'
    const randomize = Boolean(document.getElementById(CONTROL_IDS.randomize)?.checked)
    const seed = document.getElementById(CONTROL_IDS.seed)?.value || '42'
    const lastSeed = document.getElementById('last-generated-seed')?.value || '--'
    const enabledOutputCount = ['protect', 'loudness']
      .filter((name) => document.getElementById(CONTROL_IDS[name])?.checked).length

    this.root.querySelector('[data-generation-summary="model"]').textContent = `${temperature} / ${topK}`
    this.root.querySelector('[data-generation-summary="seed"]').textContent = randomize
      ? this.randomLabel
      : seed
    this.root.querySelector('[data-generation-summary="output"]').textContent = `${enabledOutputCount}/2`
    this.root.querySelector('[data-generation-summary="last-seed"]').textContent = lastSeed
    this.root.querySelector('[data-generation-proxy="seed"]').disabled = randomize
  }
}
