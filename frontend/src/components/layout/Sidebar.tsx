import { NavLink } from "react-router-dom"
import { LayoutDashboard, Users, BookOpen, Map, Settings, Briefcase, GraduationCap, Bot } from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Labour Market', href: '/labour-market', icon: Briefcase },
  { name: 'Skills', href: '/skills', icon: BookOpen },
  { name: 'Curriculum', href: '/curriculum', icon: BookOpen },
  { name: 'Districts', href: '/districts', icon: Map },
  { name: 'Students', href: '/students', icon: Users },
  { name: 'Training', href: '/training', icon: GraduationCap },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="w-64 border-r bg-card hidden md:flex flex-col">
      <div className="h-16 flex items-center px-6 border-b">
        <span className="font-bold text-xl tracking-tighter">NEXORA</span>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )
            }
          >
            <item.icon className="w-4 h-4" />
            {item.name}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
