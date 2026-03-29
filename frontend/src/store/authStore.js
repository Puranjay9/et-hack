import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
    persist(
        (set, get) => ({
            accessToken: null,
            refreshToken: null,
            user: null,
            isAuthenticated: false,

            setTokens: (accessToken, refreshToken) =>
                set({ accessToken, refreshToken, isAuthenticated: true }),

            setUser: (user) => set({ user }),

            logout: () =>
                set({
                    accessToken: null,
                    refreshToken: null,
                    user: null,
                    isAuthenticated: false,
                }),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
        }
    )
)
