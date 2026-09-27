import AMapLoader from '@amap/amap-jsapi-loader'
import type { Location } from './types'

// The vendor loader exposes an untyped SDK. Keep its dynamic boundary in this module.
export type AMapSDK = any
export type AMapObject = any
let loading: Promise<AMapSDK> | null = null
export const mapConfigured = Boolean(import.meta.env.VITE_AMAP_KEY?.trim())
export const mapUnavailable = '地图暂不可用，可手动填写地点'

export function withTimeout<T>(promise: Promise<T>, ms = 10000): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error('请求超时，请重试或手动填写地点')), ms)
    promise.then(value => { clearTimeout(timer); resolve(value) }, error => { clearTimeout(timer); reject(error) })
  })
}
export function loadMap(): Promise<AMapSDK> {
  if (!mapConfigured) return Promise.reject(new Error(mapUnavailable))
  if (loading) return loading
  loading = (async () => {
    const base = new URL(import.meta.env.VITE_AMAP_SERVICE_HOST || '/_AMapService', window.location.origin)
    if (base.origin !== window.location.origin || !base.pathname.endsWith('/_AMapService')) throw new Error(mapUnavailable)
    const response = await fetch(`${base.href}/status`, { signal: AbortSignal.timeout(5000), credentials: 'omit' })
    if (!response.ok || !(await response.json()).enabled) throw new Error(mapUnavailable)
    ;(window as Window & { _AMapSecurityConfig?: object })._AMapSecurityConfig = { serviceHost: base.href }
    return withTimeout(AMapLoader.load({ key: import.meta.env.VITE_AMAP_KEY, version:'2.0', plugins: [
      'AMap.AutoComplete','AMap.PlaceSearch','AMap.Geocoder','AMap.Geolocation',
    ] }), 12000)
  })().catch(error => { loading = null; (AMapLoader as typeof AMapLoader & { reset: () => void }).reset(); throw error })
  return loading
}
export function sdkCall(run: (callback: (status: string, result: any) => void) => void): Promise<any> {
  return withTimeout(new Promise((resolve, reject) => run((status, result) => {
    if (status === 'complete') resolve(result)
    else if (status === 'no_data') resolve({ tips: [], poiList: { pois: [] } })
    else reject(new Error('未能获取地图信息，请重试或手动选择'))
  })))
}
export function locationOf(position: AMapObject, source: Location['source'], address = '', poiId: string | null = null, adcode: string | null = null): Location {
  const longitude = Number(position?.lng ?? position?.getLng?.())
  const latitude = Number(position?.lat ?? position?.getLat?.())
  if (!Number.isFinite(longitude) || !Number.isFinite(latitude) || Math.abs(longitude)>180 || Math.abs(latitude)>90) throw new Error('此建议没有具体坐标，请搜索具体地点或在地图上选点')
  return { longitude: Number(longitude.toFixed(6)), latitude: Number(latitude.toFixed(6)), address: address.slice(0,300), source,
    poi_id: poiId || null, adcode: adcode && /^\d{6}$/.test(adcode) ? adcode : null, coordinate_system:'gcj02' }
}
