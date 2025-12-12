"use client"

import { useEffect, useRef } from 'react'
import { useAuth } from '@/context/AuthContext'
import { usePlayer } from '@/context/PlayerContext'

export function PlayerAuthSync() {
  const { token, user } = useAuth()
  const { resetPlayer } = usePlayer()

  // 변경 감지를 위한 이전 사용자/토큰 추적
  const prevUserRef = useRef(user?.username);
  const prevTokenRef = useRef(token);

  useEffect(() => {
    const currentUser = user?.username;
    const currentToken = token;
    const prevUser = prevUserRef.current;
    const prevToken = prevTokenRef.current;

    // 케이스 1: 로그아웃 (토큰이 null이 됨)
    if (prevToken && !currentToken) {
      resetPlayer();
    }

    // 케이스 2: 사용자 변경 (계정 전환)
    if (prevUser && currentUser && prevUser !== currentUser) {
      resetPlayer();
    }

    // Refs 업데이트
    prevUserRef.current = currentUser;
    prevTokenRef.current = currentToken;
  }, [token, user, resetPlayer]);

  return null; // 이 컴포넌트는 아무것도 렌더링하지 않음
}
