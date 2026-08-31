import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"

export default function RootLayout() {
  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Placeholder for future Navbar/Header */}
        <header className="h-16 border-b flex items-center px-6 sticky top-0 bg-background/95 backdrop-blur z-10">
          <h1 className="text-lg font-semibold tracking-tight">NEXORA</h1>
        </header>
        <main className="flex-1 p-6 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
