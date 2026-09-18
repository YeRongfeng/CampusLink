export function safeRedirect(value: unknown): string {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || /[\\\u0000-\u0020]/.test(value)) return '/'
  try {
    const url = new URL(value, window.location.origin)
    if (url.origin !== window.location.origin || ['/login', '/register'].includes(url.pathname)) return '/'
    return url.pathname + url.search + url.hash
  } catch { return '/' }
}
