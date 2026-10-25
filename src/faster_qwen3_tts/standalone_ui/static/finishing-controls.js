import { t } from './i18n.js'

const FIELDS = [
  ['high_pass_hz', 'High-pass (Hz)', 50, 150, 5, 50],
  ['warmth_db', 'Warmth (dB)', -4, 6, .5, null],
  ['warmth_hz', 'Warmth frequency (Hz)', 80, 250, 10, null],
  ['mud_db', 'Mud reduction (dB)', -5, 0, .5, 0],
  ['mud_hz', 'Mud frequency (Hz)', 180, 500, 10, 300],
  ['presence_hz', 'Presence frequency (Hz)', 2000, 5000, 100, null],
  ['air_db', 'Air (dB)', -3, 3, .5, 0],
  ['air_hz', 'Air frequency (Hz)', 7000, 11000, 500, 10000],
  ['compression_ratio', 'Compression ratio', 1, 5, .1, null],
  ['compression_threshold_dbfs', 'Compression threshold (dBFS)', -36, -8, 1, -22],
  ['compression_attack_ms', 'Compression attack (ms)', 3, 40, 1, 12],
  ['compression_release_ms', 'Compression release (ms)', 50, 300, 10, 120],
  ['deesser_strength_percent', 'De-essing (%)', 0, 100, 5, null],
  ['saturation_blend_percent', 'Saturation (%)', 0, 20, 1, 0],
  ['room_percent', 'Room (%)', 0, 10, 1, 0],
  ['target_loudness_lufs', 'Target loudness (LUFS)', -24, -14, 1, -16],
  ['peak_ceiling_dbtp', 'Peak ceiling (dBTP)', -3, -.5, .1, -1.5],
]

export class FinishingControls {
  constructor(panel, before, onChange) {
    this.inputs = new Map()
    const section = document.createElement('details')
    const summary = document.createElement('summary')
    summary.textContent = t('finishing.advancedMastering', {}, 'Advanced mastering')
    const grid = document.createElement('div'); grid.className = 'finishing-control-grid'
    for (const [key, title, min, max, step, initial] of FIELDS) {
      const label = document.createElement('label'); label.className = 'compact-field'
      const text = document.createElement('span'); text.textContent = t(`finishing.${key}`, {}, title)
      const input = document.createElement('input')
      Object.assign(input, { type: 'number', min, max, step, value: initial ?? '',
        required: initial !== null,
        placeholder: initial === null ? t('finishing.inherit', {}, 'Preset default') : '' })
      input.addEventListener('input', onChange)
      this.inputs.set(key, input)
      label.append(text, input); grid.append(label)
    }
    section.append(summary, grid)
    panel.insertBefore(section, before)
  }

  options() {
    return Object.fromEntries([...this.inputs].map(([key, input]) => [key, input.value === '' ? null : Number(input.value)]))
  }

  restore(options = {}) {
    for (const [key, , , , , initial] of FIELDS) {
      this.inputs.get(key).value = Object.hasOwn(options, key) ? options[key] ?? '' : initial ?? ''
    }
  }

  valid() {
    for (const input of this.inputs.values()) if (!input.reportValidity()) return false
    return true
  }
}
