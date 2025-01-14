import axios from 'axios'
import utils from '@/api/api-utils'

export function updateAsset(assetId, categoryId, description, title) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/update`, {
    assetId,
    categoryId,
    description,
    title
  })
}

export function bookmarkletCreateFileAsset(categoryId, description, title, url) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/create`, {
    bookmarklet: true,
    categoryId,
    description,
    title,
    type: 'file',
    url
  })
}

export function createLinkAsset(
  categoryId: number,
  description: string,
  title: string,
  url: string,
  visible: boolean = true
) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/create`, {
    categoryId,
    description,
    title,
    type: 'link',
    url,
    visible
  })
}

export function createFileAsset(
  categoryId: number,
  description: string,
  title: string,
  file,
  visible: boolean = true
) {
  const type = 'file'
  return utils.postMultipartFormData(`${utils.apiBaseUrl()}/api/asset/create`, {
    categoryId,
    description,
    'file[0]': file,
    title,
    type,
    visible
  })
}

export function deleteAsset(assetId) {
  return axios.delete(`${utils.apiBaseUrl()}/api/asset/${assetId}/delete`)
}

export function getAsset(assetId) {
  return axios.get(`${utils.apiBaseUrl()}/api/asset/${assetId}`)
}

export function getAssets(
  assetType,
  categoryId,
  keywords,
  limit,
  offset,
  orderBy,
  sectionId,
  userId
) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/assets`,
    {
      assetType,
      categoryId,
      keywords,
      limit,
      offset,
      orderBy,
      sectionId,
      userId
    }
  )
}

export function likeAsset(assetId) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/${assetId}/like`)
}

export function refreshAssetPreview(assetId) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/${assetId}/refresh_preview`)
}

export function removeLikeAsset(assetId) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/${assetId}/remove_like`)
}
