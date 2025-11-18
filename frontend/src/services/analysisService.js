import api from './api'

/**
 * Analyze a token contract
 * @param {string} address - Contract address
 * @param {string} chain - Blockchain network
 * @param {boolean} forceRefresh - Force refresh cached data
 * @returns {Promise} Analysis result
 */
export const analyzeToken = async (address, chain = 'ethereum', forceRefresh = false) => {
  const response = await api.post(`/api/analyze/${address}`, null, {
    params: { chain, force_refresh: forceRefresh }
  })
  return response.data
}

/**
 * Quick check of a token (cached data only)
 * @param {string} address - Contract address
 * @param {string} chain - Blockchain network
 * @returns {Promise} Quick check result
 */
export const quickCheck = async (address, chain = 'ethereum') => {
  const response = await api.get(`/api/analyze/${address}/quick`, {
    params: { chain }
  })
  return response.data
}
