import { defineStore } from 'pinia'
import apiClient from '../api/client'

export const useWalletStore = defineStore('wallet', {
  state: () => ({
    wallets: [],
    loading: false,
    error: null,
  }),

  getters: {
    totalBalance: (state) => {
      return state.wallets.reduce((total, wallet) => {
        return total + Number(wallet.balance || 0)
      }, 0)
    },
    getWalletById: (state) => (id) => {
      return state.wallets.find((w) => w.id === id)
    },
  },

  actions: {
    async fetchWallets() {
      this.loading = true
      this.error = null
      try {
        const response = await apiClient.get('/wallets/')
        this.wallets = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat daftar dompet'
        console.error('fetchWallets error:', err)
      } finally {
        this.loading = false
      }
    },

    async createWallet(payload) {
      this.loading = true
      try {
        const response = await apiClient.post('/wallets/', payload)
        this.wallets.push(response.data)
        return response.data
      } catch (err) {
        console.error('createWallet error:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async updateWallet(walletId, payload) {
      this.loading = true
      try {
        const response = await apiClient.patch(`/wallets/${walletId}/`, payload)
        const idx = this.wallets.findIndex((w) => w.id === walletId)
        if (idx !== -1) {
          this.wallets[idx] = response.data
        }
        return response.data
      } catch (err) {
        console.error('updateWallet error:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteWallet(walletId) {
      this.loading = true
      try {
        const response = await apiClient.delete(`/wallets/${walletId}/`)
        this.wallets = this.wallets.filter((w) => w.id !== walletId)
        return response.data
      } catch (err) {
        console.error('deleteWallet error:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    syncWallet(updatedWallet) {
      if (!updatedWallet) return
      const idx = this.wallets.findIndex((w) => w.id === updatedWallet.id)
      if (idx !== -1) {
        this.wallets[idx] = { ...this.wallets[idx], ...updatedWallet }
      } else {
        this.wallets.push(updatedWallet)
      }
    },

    updateBalanceOptimistic(walletId, diffAmount) {
      const wallet = this.wallets.find((w) => w.id === walletId)
      if (wallet) {
        const newBal = Number(wallet.balance) + Number(diffAmount)
        wallet.balance = newBal.toFixed(2)
      }
    },

    setWalletsState(snapshot) {
      this.wallets = JSON.parse(JSON.stringify(snapshot))
    },
  },
})
