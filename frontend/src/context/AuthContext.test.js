import { renderHook, act } from '@testing-library/react-hooks';
import { AuthProvider, useAuth } from './AuthContext';
import React from 'react';

describe('AuthContext', () => {
  it('permite login y logout', () => {
    const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
    const { result } = renderHook(() => useAuth(), { wrapper });
    act(() => {
      result.current.login({ sub: 'usuario', role: 'user' }, 'token123');
    });
    expect(result.current.user).toEqual({ sub: 'usuario', role: 'user' });
    expect(result.current.token).toBe('token123');
    act(() => {
      result.current.logout();
    });
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });
});
