'use client'

import { Button } from "@/components/ui/button"

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    return (
        <html>
            <body>
                <div className="flex h-screen flex-col items-center justify-center gap-4">
                    <h2 className="text-2xl font-bold">Global Error</h2>
                    <p className="text-muted-foreground">Something critically wrong happened.</p>
                    <Button onClick={() => reset()}>Try again</Button>
                </div>
            </body>
        </html>
    )
}
