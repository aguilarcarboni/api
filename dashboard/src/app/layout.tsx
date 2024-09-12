import './globals.css'
import type { Metadata } from 'next'
import { cn } from '@/lib/utils'
import { Inter } from 'next/font/google'
 
export const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'laserfocus API',
  description: '',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={cn(inter.className,'flex overflow-x-hidden h-fit no-scrollbar justify-center items-start scroll-smooth w-full min-h-full min-w-full')} >
      <body className='w-full h-full no-scrollbar bg-white flex flex-col justify-center items-center p-10'>
          {children}
      </body>
    </html>
  )
}