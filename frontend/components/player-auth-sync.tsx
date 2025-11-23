"use client"

import { useEffect, useRef } from 'react'
import { useAuth } from '@/context/AuthContext'
import { usePlayer } from '@/context/PlayerContext'

export function PlayerAuthSync() {
  const { token, user } = useAuth()
  const { resetPlayer } = usePlayer()
  
  // Keep track of the previous user/token to detect changes
  const prevUserRef = useRef(user?.username);
  const prevTokenRef = useRef(token);

  useEffect(() => {
    const currentUser = user?.username;
    const currentToken = token;
    const prevUser = prevUserRef.current;
    const prevToken = prevTokenRef.current;

    // Case 1: Logout (Token became null)
    if (prevToken && !currentToken) {
      resetPlayer();
    }
    
    // Case 2: User changed (Switched accounts)
    if (prevUser && currentUser && prevUser !== currentUser) {
      resetPlayer();
    }

    // Update refs
    prevUserRef.current = currentUser;
    prevTokenRef.current = currentToken;
  }, [token, user, resetPlayer]);

  return null; // This component renders nothing
}
