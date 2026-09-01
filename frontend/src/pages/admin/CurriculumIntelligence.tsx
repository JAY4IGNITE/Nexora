import { useState, useEffect } from "react"
import { LayoutList, BarChart3, AlertTriangle, Briefcase, GraduationCap, Server } from "lucide-react"

export default function CurriculumIntelligence() {
  const [overview, setOverview] = useState<any>(null)
  const [alignment, setAlignment] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      const [overviewRes, alignmentRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/curriculum/overview").then(res => res.json()),
        fetch("http://localhost:8000/api/v1/curriculum/alignment?limit=20").then(res => res.json())
      ])
      setOverview(overviewRes)
      setAlignment(alignmentRes || [])
    } catch (e) {
      console.error("Failed to fetch curriculum data", e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  if (loading) return <div className="p-8 text-center animate-pulse">Loading intelligence...</div>

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Curriculum & Training Intelligence</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Evidence-based analysis of industry demand vs. institutional supply. 
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 mb-2">
            <GraduationCap className="w-5 h-5" />
            <h3 className="font-medium">Indexed Curricula</h3>
          </div>
          <p className="text-4xl font-semibold">{overview?.total_curricula || 0}</p>
        </div>
        
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 mb-2">
            <Server className="w-5 h-5" />
            <h3 className="font-medium">Training Programs</h3>
          </div>
          <p className="text-4xl font-semibold">{overview?.total_training_programs || 0}</p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 mb-2">
            <BarChart3 className="w-5 h-5 text-indigo-500" />
            <h3 className="font-medium">Skills Currently Covered</h3>
          </div>
          <p className="text-4xl font-semibold text-indigo-600 dark:text-indigo-400">{overview?.skills_covered || 0}</p>
        </div>
      </div>

      {/* Alignment Table */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
          <LayoutList className="w-5 h-5 text-slate-500" />
          <h2 className="font-semibold text-lg">Skill Alignment & Gap Classification</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 dark:bg-slate-900/50">
              <tr>
                <th className="px-6 py-4 font-medium">Skill</th>
                <th className="px-6 py-4 font-medium">Category</th>
                <th className="px-6 py-4 font-medium text-center">Industry Demand</th>
                <th className="px-6 py-4 font-medium text-center">Curriculum Supply</th>
                <th className="px-6 py-4 font-medium text-center">Training Supply</th>
                <th className="px-6 py-4 font-medium text-center">Priority Score</th>
                <th className="px-6 py-4 font-medium">Classification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {alignment.map((row) => (
                <tr key={row.skill_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900 dark:text-white">{row.skill_name}</td>
                  <td className="px-6 py-4 text-slate-500">{row.skill_category}</td>
                  <td className="px-6 py-4 text-center font-mono text-slate-700 dark:text-slate-300">{row.industry_demand_count}</td>
                  <td className="px-6 py-4 text-center font-mono">{row.curriculum_program_count}</td>
                  <td className="px-6 py-4 text-center font-mono">{row.training_program_count}</td>
                  <td className="px-6 py-4 text-center font-mono text-indigo-500">{row.gap_priority.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                      row.classification === 'ALIGNED' ? 'bg-green-100 text-green-700 border border-green-200' :
                      row.classification === 'UNDER_COVERED' ? 'bg-orange-100 text-orange-700 border border-orange-200' :
                      row.classification === 'NOT_COVERED' ? 'bg-rose-100 text-rose-700 border border-rose-200' :
                      'bg-slate-100 text-slate-700 border border-slate-200'
                    }`}>
                      {row.classification === 'ALIGNED' && <CheckCircle className="w-3 h-3" />}
                      {row.classification === 'UNDER_COVERED' && <Briefcase className="w-3 h-3" />}
                      {row.classification === 'NOT_COVERED' && <AlertTriangle className="w-3 h-3" />}
                      {row.classification.replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
              {alignment.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    No alignment data available. Trigger Adzuna sync to generate demand.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  )
}
