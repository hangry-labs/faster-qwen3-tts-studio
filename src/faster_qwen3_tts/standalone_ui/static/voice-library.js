import { msg, languageLabel } from './i18n.js'
// Shared audio-backed library for Qwen Design, Clone and Generate.
import { closeDialogOnBackdrop } from './dialog-utils.js'

const $ = selector => document.querySelector(selector)

export function voiceRecipe(context, finishing, selectedVersion = 'original') {
  const recipe = structuredClone(context.recipe || {})
  recipe.version = 1
  recipe.selected_version = selectedVersion
  if (Number.isInteger(context.metrics?.seed)) {
    recipe.settings ||= {}
    recipe.settings.seed = context.metrics.seed
    recipe.settings.randomize_seed = false
  }
  recipe.finishing = structuredClone({ options: finishing.options || {}, processedOptions: finishing.processedOptions,
    stale: !!finishing.stale })
  return recipe
}

export function canReplaceVoice(context, refinement) {
  return !!refinement && Number.isFinite(context.generatedAt) && context.generatedAt > refinement.startedAt
}

export function refinementDocument(source, existingNames) {
  const xml = new DOMParser().parseFromString(source, 'application/xml')
  if (xml.querySelector('parsererror')) throw new Error(msg('Saved creation markup is invalid.'))
  const occupied = new Set(existingNames.map(value => value.toLowerCase()))
  const definitions = [...xml.getElementsByTagNameNS('https://hangrylabs.app/ns/ssml-h/1.0', 'voice-definition')]
  for (const node of definitions) occupied.add(node.getAttribute('name').toLowerCase())
  const existing = new Set(existingNames.map(value => value.toLowerCase()))
  for (const node of definitions) {
    const old = node.getAttribute('name')
    node.setAttribute('scope', 'request'); node.setAttribute('replace', 'false')
    if (!existing.has(old.toLowerCase())) continue
    let next, index = 0
    do { next = old.slice(0, 48) + '-refine' + (++index) } while (occupied.has(next.toLowerCase()))
    occupied.add(next.toLowerCase()); node.setAttribute('name', next)
    for (const voice of xml.getElementsByTagNameNS('http://www.w3.org/2001/10/synthesis', 'voice')) {
      if ((voice.getAttribute('name') || '').toLowerCase() === old.toLowerCase()) voice.setAttribute('name', next)
    }
  }
  return new XMLSerializer().serializeToString(xml.documentElement)
}

export class VoiceLibrary {
  constructor({ fetchJson, toast, capture, onUse, onRefine, onRefresh, isBusy }) {
    Object.assign(this, { fetchJson, toast, capture, onUse, onRefine, onRefresh, isBusy })
    this.records = []; this.refinement = null
    $('#end-refinement').addEventListener('click', () => this.finishRefinement())
    $('#voice-filter').addEventListener('input', () => this.render())
    $('#refresh-voices').addEventListener('click', () => this.refresh().catch(error => toast(error.message)))
    $('#close-save').addEventListener('click', () => $('#save-voice-dialog').close())
    closeDialogOnBackdrop($('#save-voice-dialog'), () => $('#save-voice-dialog').close())
    $('#save-voice-dialog').addEventListener('close', () => this.revokePortrait())
    $('#voice-portrait').addEventListener('change', () => {
      this.revokePortrait()
      const file = $('#voice-portrait').files[0]
      if (file) { this.portraitUrl = URL.createObjectURL(file); $('#voice-portrait-preview').src = this.portraitUrl }
      $('#voice-portrait-preview').hidden = !file
      if (file) $('#voice-clear-portrait').checked = false
    })
    $('#save-voice-form').addEventListener('submit', event => { event.preventDefault(); this.save() })
  }

  revokePortrait() { if (this.portraitUrl) URL.revokeObjectURL(this.portraitUrl); this.portraitUrl = null }

  async refresh() {
    const { data } = await this.fetchJson('/tts/voice-profiles')
    this.records = data; this.render(); await this.onRefresh()
  }

  render() {
    const needle = $('#voice-filter').value.trim().toLocaleLowerCase()
    const records = this.records.filter(v => [v.name, v.description, v.language, ...(v.tags || [])].join(' ').toLocaleLowerCase().includes(needle))
    $('#voice-count').textContent = `${records.length}${records.length !== this.records.length ? ' / ' + this.records.length : ''}`
    const list = $('#voice-library'); list.replaceChildren()
    if (!records.length) {
      const empty = document.createElement('p'); empty.className = 'clone-profile-empty'
      empty.textContent = this.records.length ? msg('No voices match this search.') : msg('Save a designed voice or permitted reference to start your library.')
      list.append(empty)
    }
    for (const voice of records) {
      const card = document.createElement('article'); card.className = 'clone-profile-card'
      if (this.refinement?.profile.id === voice.id) card.classList.add('editing')
      const copy = document.createElement('div'); copy.className = 'clone-profile-copy'
      const name = document.createElement('strong'); name.textContent = voice.name
      const description = document.createElement('span'); description.textContent = voice.description || voice.ref_text || msg('Audio reference')
      copy.append(name, description)
      const portrait = document.createElement('button'); portrait.type = 'button'; portrait.className = 'clone-profile-portrait'
      portrait.setAttribute('aria-label', msg`Edit portrait for ${voice.name}`)
      if (voice.portrait_url) {
        const img = document.createElement('img'); img.src = voice.portrait_url + '?v=' + encodeURIComponent(voice.updated_at || ''); img.alt = ''; img.loading = 'lazy'; portrait.append(img)
      } else portrait.textContent = voice.name.slice(0, 1).toUpperCase()
      portrait.addEventListener('click', () => this.edit(voice))
      const tags = document.createElement('div'); tags.className = 'clone-profile-metadata'
      const typeLabel = { design: msg('Voice design'), clone: msg('Voice clone'), reference: msg('Audio reference') }[voice.profile_type] || voice.profile_type
      for (const text of [languageLabel(voice.language), typeLabel, ...(voice.tags || [])]) {
        const span = document.createElement('span'); span.textContent = text; tags.append(span)
      }
      const audio = document.createElement('audio'); audio.controls = true; audio.preload = 'none'; audio.src = voice.audio_url
      audio.className = 'clone-profile-audio'; audio.setAttribute('aria-label', msg`Preview ${voice.name}`)
      audio.addEventListener('play', () => list.querySelectorAll('audio').forEach(other => { if (other !== audio) other.pause() }))
      const actions = document.createElement('div'); actions.className = 'voice-card-actions'
      for (const [label, action] of [
        [msg('Use voice'), () => this.onUse(voice)],
        [msg('Refine'), async () => {
          await this.onRefine(voice); this.refinement = { profile: voice, startedAt: performance.now() }
          $('#voice-refinement-label').textContent = msg`Refining ${voice.name}. Generate fresh audio before replacing its saved reference.`
          $('#voice-refinement').hidden = false; this.render()
        }],
        [msg('Edit details'), () => this.edit(voice)],
        [msg('Delete'), async () => {
          if (!confirm(msg`Delete the saved voice “${voice.name}” and its saved assets?`)) return
          await this.fetchJson('/tts/voice-profiles/' + voice.id, { method: 'DELETE' })
          if (this.refinement?.profile.id === voice.id) this.finishRefinement()
          await this.refresh()
        }],
      ]) {
        const button = document.createElement('button'); button.type = 'button'; button.className = 'secondary-button compact-command'; button.textContent = label
        button.addEventListener('click', async () => {
          if (this.isBusy() || this.working) return this.toast(msg('Wait for the current operation to finish first.'))
          button.disabled = true; this.working = true
          const generation = $('#generate-button'), disabled = generation.disabled
          generation.disabled = true
          try { await action() } catch (error) { this.toast(error.message) }
          finally { button.disabled = false; this.working = false; generation.disabled = disabled }
        }); actions.append(button)
      }
      card.append(copy, portrait, tags, audio, actions); list.append(card)
    }
  }

  finishRefinement() {
    this.refinement = null; $('#voice-refinement').hidden = true; this.render()
  }

  relocalize() {
    this.render()
    if (this.refinement) $('#voice-refinement-label').textContent = msg`Refining ${this.refinement.profile.name}. Generate fresh audio before replacing its saved reference.`
    if ($('#save-voice-dialog').open) {
      $('#save-voice-title').textContent = this.editing ? msg('Edit voice details') : msg('Save voice reference')
      $('#save-voice-help').textContent = this.editing
        ? msg('Update metadata and portrait. The saved audio and creation settings stay intact.')
        : msg('Store the selected reference, original recording, source reference and creation settings. A processed recording is available only when its preview matches the current settings.')
      $('#voice-submit').textContent = this.editing ? msg('Save details') : msg('Save voice')
    }
  }

  fill(profile = {}) {
    this.revokePortrait()
    $('#voice-name').value = profile.name || ''
    $('#voice-transcript').value = profile.ref_text || ''
    $('#voice-description').value = profile.description || ''
    $('#voice-tags').value = (profile.tags || []).join(', ')
    $('#voice-language').value = profile.language || 'English'
    $('#voice-portrait').value = ''; $('#voice-clear-portrait').checked = false; $('#voice-replace').checked = false
    $('#voice-portrait-preview').hidden = !profile.portrait_url
    if (profile.portrait_url) $('#voice-portrait-preview').src = profile.portrait_url
    $('#voice-clear-portrait-field').hidden = !profile.portrait_url
    $('#voice-save-error').hidden = true
  }

  edit(profile) {
    if (this.isBusy()) return this.toast(msg('Wait for generation to finish first.'))
    this.editing = profile; this.context = null
    this.fill(profile)
    $('#save-voice-title').textContent = msg('Edit voice details')
    $('#save-voice-help').textContent = msg('Update metadata and portrait. The saved audio and creation settings stay intact.')
    $('#voice-version-field').hidden = true; $('#voice-replace-field').hidden = true
    $('#voice-submit').textContent = msg('Save details')
    $('#save-voice-dialog').showModal(); $('#voice-name').focus()
  }

  open(file, transcript, context = null) {
    if (!file || this.isBusy()) return
    this.editing = null
    this.context = context || this.capture()
    this.context = { ...this.context, file, transcript }
    const refining = canReplaceVoice(this.context, this.refinement) ? this.refinement.profile : null
    this.context.inheritedPortrait = refining?.portrait_url
    this.fill(refining || {})
    $('#voice-transcript').value = transcript || ''
    $('#voice-language').value = this.context.recipe?.settings?.language || 'English'
    $('#voice-version-field').hidden = false
    const processed = this.context.finishing?.processed && !this.context.finishing.stale
    $('#voice-version').querySelector('[value=processed]').disabled = !processed
    $('#voice-version').value = 'original'
    $('#voice-replace-field').hidden = !refining
    $('#save-voice-title').textContent = msg('Save voice reference')
    $('#save-voice-help').textContent = msg('Store the selected reference, original recording, source reference and creation settings. A processed recording is available only when its preview matches the current settings.')
    $('#voice-submit').textContent = msg('Save voice')
    $('#save-voice-dialog').showModal(); $('#voice-name').focus()
  }

  async save() {
    const button = $('#voice-submit'); button.disabled = true
    try {
      const form = new FormData()
      for (const [field, id] of [['name', 'voice-name'], ['ref_text', 'voice-transcript'], ['description', 'voice-description'], ['language', 'voice-language']]) form.set(field, $('#' + id).value)
      form.set('tags', JSON.stringify($('#voice-tags').value.split(',').map(t => t.trim()).filter(Boolean)))
      const portrait = $('#voice-portrait').files[0]
      if (portrait) form.set('portrait', portrait)
      else if (!this.editing && !$('#voice-replace').checked && !$('#voice-clear-portrait').checked && this.context.inheritedPortrait) {
        const response = await fetch(this.context.inheritedPortrait, { cache: 'no-store' })
        if (!response.ok) throw new Error(msg('The original portrait could not be loaded for this copy.'))
        form.set('portrait', await response.blob(), 'portrait.webp')
      }
      form.set('clear_portrait', String($('#voice-clear-portrait').checked))
      let target = this.editing
      if (!target) {
        const context = this.context, finishing = context.finishing || { options: {} }
        const version = $('#voice-version').value
        if (version === 'processed' && (!finishing.processed || finishing.stale)) throw new Error(msg('Create a current processed preview first.'))
        const original = context.original || context.file
        const selected = version === 'processed' ? finishing.processed.blob : original
        form.set('reference_audio', selected, 'reference.wav'); form.set('original_audio', original, 'original.wav')
        if (finishing.processed && !finishing.stale) form.set('processed_audio', finishing.processed.blob, 'processed.wav')
        if (context.source) form.set('design_audio', context.source, 'source.wav')
        form.set('recipe', JSON.stringify(voiceRecipe(context, finishing, version)))
        form.set('profile_type', context.recipe?.workflow === 'design' ? 'design' : context.recipe?.workflow === 'reference' ? 'reference' : 'clone')
        if ($('#voice-replace').checked) {
          if (!canReplaceVoice(context, this.refinement)) throw new Error(msg('Generate fresh audio before replacing a saved voice.'))
          target = this.refinement.profile
          if (!confirm(msg`Replace the saved voice “${target.name}” with this newly generated recording?`)) return
          form.set('replace_audio', 'true')
        }
      }
      await this.fetchJson('/tts/voice-profiles' + (target ? '/' + target.id : ''), { method: target ? 'PUT' : 'POST', body: form })
      $('#save-voice-dialog').close(); this.finishRefinement()
      await this.refresh(); this.toast(target ? msg('Voice updated in your local library.') : msg('Voice saved to your local library.'))
    } catch (error) {
      $('#voice-save-error').textContent = error.message; $('#voice-save-error').hidden = false
    } finally { button.disabled = false }
  }
}
