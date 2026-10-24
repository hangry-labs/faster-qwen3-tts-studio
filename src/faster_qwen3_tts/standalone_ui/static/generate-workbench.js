// Qwen adapter for the shared VoxCPMTTS dialogue editor and workspace contracts.
import { MagicEditor } from './magic-editor.js'
import { MagicTakeStudio } from './magic-takes.js'
import { DialogueScriptLibrary } from './dialogue-script-library.js'
import { renderedSpeechText, serializeMagicDocument } from './magic-document.js'
import { encodeWav } from './audio-utils.js'
import { decodePcmWav, PcmPlayer } from './pcm-player.js'

const $ = selector => document.querySelector(selector)

export class GenerateWorkbench {
  constructor({ options, fetchJson, toast, onOutput, onBusy, onMetrics }) {
    Object.assign(this, { options, fetchJson, toast, onOutput, onBusy, onMetrics })
    this.inputType = 'magic'
    this.controller = null
    this.library = null
    this.output = null
    this.takes = new MagicTakeStudio({ responseError: async response => {
      const data = await response.json()
      return typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    } })
    this.editor = new MagicEditor($('#magic-editor-shell'), {
      onChange: () => { this.count(); this.library?.markDirty() },
      onPreview: block => this.job(async signal => {
        const index = this.editor.speechBlocks().findIndex(item => item.id === block.id)
        return this.takes.take(this.payload(), index, { signal })
      }),
      onSaveCharacter: async block => {
        const name = prompt('Save this generated voice as:')?.trim()
        if (!name) return
        const preview = await this.editor.ensurePreview(block.id)
        const form = new FormData()
        form.set('name', name); form.set('transcript', renderedSpeechText(block)); form.set('file', preview.blob, 'voice.wav')
        await fetchJson('/studio/voices', { method: 'POST', body: form })
        await this.refreshVoices()
        toast('Voice saved. It is available to the API and other dialogue turns.')
      },
      onPersistCharacter: async ({ definition, block }) => {
        if (!block.preview?.blob) throw new Error('Generate a character turn before saving its voice.')
        const form = new FormData()
        form.set('name', definition.name); form.set('ref_text', renderedSpeechText(block))
        form.set('reference_audio', block.preview.blob, 'voice.wav')
        form.set('description', definition.description || '')
        const profile = await fetchJson('/tts/voice-profiles', { method: 'POST', body: form })
        await this.refreshVoices()
        return { profileId: profile.id }
      },
      onError: error => toast(error.message || error),
      onHistoryChange: history => {
        $('#dialogue-undo').disabled = !history.canUndo
        $('#dialogue-redo').disabled = !history.canRedo
      },
    })
    this.library = new DialogueScriptLibrary({ magicEditor: this.editor, fetchJson, showToast: toast,
      errorMessage: error => error.message || String(error), getInputType: () => this.inputType,
      setInputType: (type, options) => this.setInputType(type, options), onDocumentChange: () => this.count(),
      captureWorkspace: () => ({ settings: this.payload(), takes: this.inputType === 'magic' ? this.editor.workspaceTakes() : [],
        output: this.output ? { blob: this.output, extension: this.outputExtension || 'wav' } : null }),
      restoreWorkspace: async workspace => {
        this.editor.restoreWorkspaceTakes(workspace.takes)
        if (workspace.output?.blob) {
          this.output = workspace.output.blob
          this.outputExtension = workspace.output.extension
          await onOutput(new File([this.output], 'qwen-dialogue.' + this.outputExtension, { type: this.output.type }), this.editor.plainText(), {})
        }
      },
      clearWorkspace: () => { this.output = null },
    })
    document.querySelectorAll('[data-input-type]').forEach(button => button.addEventListener('click', () => {
      try { this.setInputType(button.dataset.inputType) } catch (error) { toast(error.message) }
    }))
    $('#text-custom').addEventListener('input', () => { this.count(); this.library.markDirty() })
    $('#dialogue-undo').addEventListener('click', () => this.editor.undoDialogue())
    $('#dialogue-redo').addEventListener('click', () => this.editor.redoDialogue())
    // Put the actual Qwen controls in the same compact toolbar positions as Vox.
    const details = $('.settings-details')
    const seed = $('#seed').closest('label'), random = $('#random-seed').closest('label')
    $('#seed-controls-popup').append(random, seed)
    for (const child of [...details.children]) if (child.tagName !== 'SUMMARY') $('#model-controls-popup').append(child)
    details.remove()
    const formatState = () => {
      $('#output-format').disabled = $('#streaming').checked
      $('#output-format').title = $('#streaming').checked ? 'Browser streaming preview and download use WAV. Choose complete generation for other formats.' : ''
    }
    $('#streaming').addEventListener('change', formatState)
    formatState()
    document.addEventListener('pointerdown', event => {
      document.querySelectorAll('.qwen-generation-toolbar details[open]').forEach(detail => {
        if (!detail.contains(event.target)) detail.open = false
      })
    })
    this.setInputType('magic', { syncSsmlH: false })
  }

  async initialize() {
    const [capabilities, scripts] = await Promise.all([this.fetchJson('/tts/ssml/capabilities'), this.fetchJson('/tts/dialogue-scripts')])
    this.editor.setCapabilities(capabilities)
    this.editor.setLanguages(['English', 'Chinese', 'Japanese', 'Korean', 'German', 'French', 'Russian', 'Portuguese', 'Spanish', 'Italian'])
    this.library.initialize(scripts.data, scripts.folders)
    await this.refreshVoices()
  }

  async refreshVoices() {
    const data = await this.fetchJson('/tts/voices')
    this.voices = [...data.saved_profiles, ...data.voices]
    this.editor.setVoices(this.voices)
    const previous = $('#saved-voice').value
    $('#saved-voice').replaceChildren(new Option('Built-in speaker', ''), ...data.saved_profiles.map(v => new Option(v.name, v.id)))
    if ([...$('#saved-voice').options].some(o => o.value === previous)) $('#saved-voice').value = previous
    this.defaultVoice()
  }

  defaultVoice() {
    const id = $('#saved-voice').value || $('#speaker').value
    this.editor.setDefaultVoice(this.voices?.find(v => v.id === id) || { id, name: id })
  }

  setInputType(type, { syncSsmlH = true } = {}) {
    if (type === 'magic' && this.inputType !== 'magic' && syncSsmlH) {
      if (this.inputType === 'text') this.loadText($('#text-custom').value)
      else this.editor.loadSSMLH($('#text-custom').value)
    } else if (this.inputType === 'magic' && type !== 'magic' && syncSsmlH) {
      $('#text-custom').value = type === 'text' ? this.editor.plainText() : this.editor.toSSMLH()
      if (type === 'ssml' && (this.editor.documentMeta.voiceDefinitions.length || this.editor.blocks.some(b => b.direction))) {
        throw new Error('This dialogue uses SSML-H characters or direction. Choose SSML-H to preserve them.')
      }
    }
    this.inputType = type
    $('#magic-editor-shell').hidden = type !== 'magic'
    $('#text-custom').hidden = type === 'magic'
    document.querySelectorAll('[data-input-type]').forEach(button => {
      button.classList.toggle('active', button.dataset.inputType === type)
      button.setAttribute('aria-pressed', String(button.dataset.inputType === type))
    })
    this.count()
  }

  count() {
    const text = this.inputType === 'magic' ? this.editor.plainText() : $('#text-custom').value
    $('#text-metrics').textContent = `${text.length} characters · ${text.trim().split(/\s+/).filter(Boolean).length} words`
    return text
  }

  loadText(text) {
    this.editor.loadSSMLH(serializeMagicDocument([{ type: 'speech', text, prosody: {} }]))
  }

  payload() {
    const base = this.options()
    const { speaker, ref_text, xvec_only, mode, ...controls } = base
    return { ...controls, mode: $('#saved-voice').value ? 'clone' : 'custom',
      voice: speaker, voice_profile: $('#saved-voice').value || null,
      text: this.inputType === 'magic' ? this.editor.toSSMLH() : $('#text-custom').value,
      input_type: this.inputType === 'magic' ? 'ssml-h' : this.inputType,
      output_format: $('#output-format').value, speed: Number($('#speech-speed').value),
      normalize_loudness: $('#normalize-loudness').checked, protect_long_audio: $('#protect-long').checked }
  }

  async job(callback) {
    if (this.controller) throw new Error('Wait for the current generation or stop it first.')
    this.controller = new AbortController()
    this.onBusy(true, this.controller)
    this.editor.setBusy(true)
    try { return await callback(this.controller.signal) }
    finally {
      this.controller = null; this.onBusy(false, null); this.editor.setBusy(false)
    }
  }

  async generate(streaming) {
    return this.job(async signal => {
      const payload = this.payload()
      $('#request-status').hidden = false
      $('#request-status').textContent = 'Preparing voice and dialogue'
      const compiled = await this.fetchJson('/tts/plan', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload), signal })
      let file, text = compiled.units.filter(unit => unit.kind === 'speech').map(unit => unit.text).join(' '), metrics = {}
      if (this.inputType === 'magic' && !streaming) {
        const result = await this.takes.render(payload, this.editor.blocks, { signal })
        this.editor.applyTakes(result.takes)
        this.editor.adoptCommittedProfiles(result.committedProfiles)
        this.output = result.output.blob; this.outputExtension = result.output.extension
        file = new File([this.output], 'qwen-dialogue.' + this.outputExtension, { type: this.output.type })
        metrics = { ...result.metrics, seed: result.requestSeed }
        await this.refreshVoices()
      } else if (streaming) {
        const response = await fetch('/tts/events', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload), signal })
        if (!response.ok) throw new Error((await response.json()).detail || 'Generation failed.')
        const player = new PcmPlayer(), parts = []
        signal.addEventListener('abort', () => player.stop().catch(() => {}), { once: true })
        await player.resume()
        let completed = false
        try {
          const reader = response.body.getReader(), decoder = new TextDecoder()
          let pending = ''
          for (;;) {
            const { value, done } = await reader.read()
            pending += decoder.decode(value || new Uint8Array(), { stream: !done })
            let boundary
            while ((boundary = pending.indexOf('\n\n')) >= 0) {
              const block = pending.slice(0, boundary); pending = pending.slice(boundary + 2)
              for (const line of block.split('\n')) {
                if (!line.startsWith('data: ')) continue
                const event = JSON.parse(line.slice(6))
                if (event.type === 'error') throw new Error(event.message)
                if (event.type === 'chunk') {
                  const { samples, rate } = decodePcmWav(Uint8Array.from(atob(event.audio_b64), c => c.charCodeAt(0)))
                  parts.push(samples); player.play(samples, rate)
                  $('#request-status').textContent = `Playing dialogue · ${event.duration_s.toFixed(2)} seconds received`
                } else if (event.type === 'turn') $('#request-status').textContent = `Generating turn ${event.index + 1} · ${event.voice}`
                else if (event.type === 'designing') $('#request-status').textContent = `Designing ${event.voice}`
                else if (event.type === 'done') {
                  completed = true; metrics = event.metrics
                  this.editor.adoptCommittedProfiles(event.committed_profiles || {})
                }
              }
            }
            if (done) break
          }
          if (!completed) throw new Error('The stream ended before completion.')
          const merged = new Float32Array(parts.reduce((n, part) => n + part.length, 0))
          let offset = 0
          for (const part of parts) { merged.set(part, offset); offset += part.length }
          file = new File([encodeWav([merged], 24000)], 'qwen-dialogue.wav', { type: 'audio/wav' })
          this.output = file; this.outputExtension = 'wav'
          await player.finish()
        } finally { await player.stop() }
      } else {
        const response = await fetch('/tts/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal })
        if (!response.ok) throw new Error((await response.json()).detail || 'Generation failed.')
        file = new File([await response.blob()], 'qwen-speech.' + payload.output_format, { type: response.headers.get('Content-Type') })
        this.output = file; this.outputExtension = payload.output_format
      }
      if (payload.output_format === 'pcm' && !streaming) {
        // Raw PCM has no header. Wrap a browser preview while retaining the API's
        // documented raw 24 kHz signed-16 output contract.
        const samples = new Int16Array(await file.arrayBuffer())
        file = new File([encodeWav([Float32Array.from(samples, v => v / 32768)], 24000)], 'qwen-preview.wav', { type: 'audio/wav' })
      }
      await this.onOutput(file, text, metrics)
      this.onMetrics(metrics)
      $('#request-status').textContent = 'Generation complete'
      await this.refreshVoices()
    })
  }
}
