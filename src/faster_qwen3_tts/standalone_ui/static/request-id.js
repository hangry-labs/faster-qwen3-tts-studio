// Request correlation also works on trusted HTTP LAN origins.
export function generateRequestId(source = globalThis.crypto) {
  if (typeof source.randomUUID === 'function') return source.randomUUID()
  const bytes = source.getRandomValues(new Uint8Array(16))
  return Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('')
}
