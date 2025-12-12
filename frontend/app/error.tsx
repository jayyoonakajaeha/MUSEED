'use client' // 에러 컴포넌트는 클라이언트 컴포넌트여야 함

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        // 에러 리포팅 서비스에 에러 로그 기록
        console.error(error)
    }, [error])

    return (
        <div className="flex h-screen flex-col items-center justify-center gap-4">
            <h2 className="text-2xl font-bold">Something went wrong!</h2>
            <p className="text-muted-foreground">{error.message || 'An unexpected error occurred'}</p>
            <Button
                onClick={
                    // 세그먼트를 재생성하여 복구 시도
                    () => reset()
                }
            >
                Try again
            </Button>
        </div>
    )
}
