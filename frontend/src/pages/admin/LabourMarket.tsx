import { useState, useEffect } from "react"
import { Play, Database, Activity, LayoutList, Layers, CheckCircle, AlertTriangle, Briefcase, TrendingUp, BarChart3, Scissors } from "lucide-react"
import { auth } from "../../lib/firebase"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend, Cell, ReferenceLine } from 'recharts'

export default function LabourMarket() {
  const [activeTab, setActiveTab] = useState<'pipeline' | 'intelligence' | 'gap'>('gap')
  
  // Pipeline State
  const [stats, setStats] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [ingesting, setIngesting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Intelligence State
  const [demandRoles, setDemandRoles] = useState<any[]>([])
  const [demandSectors, setDemandSectors] = useState<any[]>([])
  const [demandSkills, setDemandSkills] = useState<any[]>([])
  const [skillTrends, setSkillTrends] = useState<any[]>([])

  // Gap State
  const [gapData, setGapData] = useState<any[]>([])

  const fetchPipelineData = async () => {
    try {
      const statsRes = await fetch("http://localhost:8000/api/v1/labour-market/statistics")
      if (statsRes.ok) setStats(await statsRes.json())

      const token = await auth.currentUser?.getIdToken()
      if (token) {
        const runsRes = await fetch("http://localhost:8000/api/v1/labour-market/ingestion-runs", {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (runsRes.ok) setRuns(await runsRes.json())
      }
    } catch (e) {
      console.error("Failed to fetch pipeline data", e)
    }
  }

  const fetchIntelligenceData = async () => {
    try {
      const [roles, sectors, skills, trends, gaps] = await Promise.all([
        fetch("http://localhost:8000/api/v1/intelligence/demand/roles?limit=5").then(res => res.json()),
        fetch("http://localhost:8000/api/v1/intelligence/demand/sectors?limit=5").then(res => res.json()),
        fetch("http://localhost:8000/api/v1/intelligence/demand/skills?limit=10").then(res => res.json()),
        fetch("http://localhost:8000/api/v1/intelligence/trends/skills?limit_skills=3").then(res => res.json()),
        fetch("http://localhost:8000/api/v1/intelligence/gap/skills?limit=15").then(res => res.json())
      ])
      setDemandRoles(roles || [])
      setDemandSectors(sectors || [])
      setDemandSkills(skills || [])
      setSkillTrends(trends || [])
      setGapData(gaps || [])
    } catch (e) {
      console.error("Failed to fetch intelligence data", e)
    }
  }

  useEffect(() => {
    fetchPipelineData()
    fetchIntelligenceData()
    const interval = setInterval(() => {
      if (activeTab === 'pipeline') fetchPipelineData()
    }, 10000)
    return () => clearInterval(interval)
  }, [activeTab])

  const handleIngest = async () => {
    setIngesting(true)
    setError(null)
    try {
      const token = await auth.currentUser?.getIdToken()
      const response = await fetch("http://localhost:8000/api/v1/labour-market/ingest?provider=adzuna", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (!response.ok) {
        const errData = await response.json()
        setError(errData.detail || "Failed to start ingestion")
      } else {
        await fetchPipelineData()
        await fetchIntelligenceData()
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setIngesting(false)
    }
  }

  const renderGapEngine = () => (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Demand-Supply Gap Engine</h2>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Identify skills with severe deficits in the workforce versus those in surplus.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Diverging Bar Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center gap-3 text-slate-800 dark:text-white mb-6">
            <Scissors className="w-5 h-5 text-rose-500" />
            <h3 className="font-semibold text-lg">Net Skill Gap (Deficit vs Surplus)</h3>
          </div>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={gapData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="skill_name" type="category" width={120} tick={{ fontSize: 12 }} />
                <Tooltip 
                  cursor={{fill: 'rgba(0,0,0,0.05)'}} 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  formatter={(value: number) => [Math.abs(value), value < 0 ? 'Deficit' : 'Surplus']}
                />
                <ReferenceLine x={0} stroke="#94a3b8" />
                <Bar dataKey="net_gap" radius={4} barSize={20}>
                  {gapData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.net_gap < 0 ? '#ef4444' : '#10b981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Deficits Table */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col">
          <div className="flex items-center gap-3 text-slate-800 dark:text-white mb-4">
            <AlertTriangle className="w-5 h-5 text-rose-500" />
            <h3 className="font-semibold text-lg">Critical Deficits</h3>
          </div>
          <div className="flex-1 overflow-y-auto pr-2">
            <div className="space-y-3">
              {gapData.filter(g => g.net_gap < 0).map((skill: any, idx: number) => (
                <div key={skill.skill_id} className="flex justify-between items-center p-3 bg-rose-50 dark:bg-rose-900/20 rounded-lg border border-rose-100 dark:border-rose-900/30">
                  <div className="flex items-center gap-3">
                    <span className="text-rose-400 font-mono text-sm">#{idx + 1}</span>
                    <div>
                      <p className="font-medium text-sm text-slate-900 dark:text-white">{skill.skill_name}</p>
                      <p className="text-xs text-slate-500">Demand: {skill.demand} | Supply: {skill.total_supply}</p>
                    </div>
                  </div>
                  <span className="bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-400 px-2 py-1 rounded text-xs font-semibold">
                    {skill.net_gap}
                  </span>
                </div>
              ))}
              {gapData.filter(g => g.net_gap < 0).length === 0 && (
                <p className="text-slate-400 text-sm">No critical deficits detected.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderPipeline = () => (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Pipeline Operations</h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Manage data ingestion and ETL tasks.</p>
        </div>
        <button 
          onClick={handleIngest} 
          disabled={ingesting}
          className="flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2 rounded-lg font-medium hover:bg-slate-800 dark:hover:bg-slate-100 transition-colors disabled:opacity-50"
        >
          {ingesting ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Trigger Adzuna Sync
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-3 border border-red-100">
          <AlertTriangle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 mb-2">
            <Database className="w-5 h-5" />
            <h3 className="font-medium">Total Postings</h3>
          </div>
          <p className="text-4xl font-semibold">{stats?.total_jobs || 0}</p>
        </div>
        
        <div className="md:col-span-2 bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
           <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 mb-4">
            <Layers className="w-5 h-5" />
            <h3 className="font-medium">Jobs by Sector</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {stats?.jobs_by_sector?.length ? stats.jobs_by_sector.map((s: any) => (
              <div key={s.sector} className="flex justify-between items-center bg-slate-50 dark:bg-slate-900 p-3 rounded-lg">
                <span className="text-sm font-medium truncate">{s.sector}</span>
                <span className="bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-white px-2 py-1 rounded text-xs font-semibold">{s.count}</span>
              </div>
            )) : <p className="text-sm text-slate-400">No data available.</p>}
          </div>
        </div>
      </div>

      {/* Runs Table */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
          <LayoutList className="w-5 h-5 text-slate-500" />
          <h2 className="font-semibold text-lg">Recent Ingestion Runs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 dark:bg-slate-900/50">
              <tr>
                <th className="px-6 py-4 font-medium">Provider</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-center">Received</th>
                <th className="px-6 py-4 font-medium text-center text-green-600">Inserted</th>
                <th className="px-6 py-4 font-medium text-center text-orange-500">Duplicate</th>
                <th className="px-6 py-4 font-medium text-center text-red-500">Rejected/Failed</th>
                <th className="px-6 py-4 font-medium">Started At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {runs.map((run) => (
                <tr key={run.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium">{run.provider}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                      run.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                      run.status === 'FAILED' ? 'bg-red-100 text-red-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {run.status === 'COMPLETED' && <CheckCircle className="w-3 h-3" />}
                      {run.status === 'FAILED' && <AlertTriangle className="w-3 h-3" />}
                      {run.status === 'RUNNING' && <Activity className="w-3 h-3 animate-pulse" />}
                      {run.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center font-mono">{run.records_received}</td>
                  <td className="px-6 py-4 text-center font-mono text-green-600">{run.records_inserted}</td>
                  <td className="px-6 py-4 text-center font-mono text-orange-500">{run.records_duplicate}</td>
                  <td className="px-6 py-4 text-center font-mono text-red-500">{run.records_rejected + run.records_failed}</td>
                  <td className="px-6 py-4 text-slate-500">{new Date(run.started_at).toLocaleString()}</td>
                </tr>
              ))}
              {runs.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    No ingestion runs yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderIntelligence = () => {
    // Generate distinct colors for skill lines
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    const trendKeys = skillTrends.length > 0 
      ? Object.keys(skillTrends[0]).filter(k => k !== 'month')
      : []

    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Market Intelligence</h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Aggregated insights and trends from ingested data.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Roles Chart */}
          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex items-center gap-3 text-slate-800 dark:text-white mb-6">
              <Briefcase className="w-5 h-5 text-blue-500" />
              <h3 className="font-semibold text-lg">Demand by Job Role</h3>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={demandRoles} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="role_name" type="category" width={120} tick={{ fontSize: 12 }} />
                  <Tooltip cursor={{fill: 'rgba(0,0,0,0.05)'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}/>
                  <Bar dataKey="demand_count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Sectors Chart */}
          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex items-center gap-3 text-slate-800 dark:text-white mb-6">
              <BarChart3 className="w-5 h-5 text-emerald-500" />
              <h3 className="font-semibold text-lg">Demand by Sector</h3>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={demandSectors} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="sector_name" type="category" width={120} tick={{ fontSize: 12 }} />
                  <Tooltip cursor={{fill: 'rgba(0,0,0,0.05)'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}/>
                  <Bar dataKey="demand_count" fill="#10b981" radius={[0, 4, 4, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Skill Trends Line Chart */}
          <div className="lg:col-span-2 bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex items-center gap-3 text-slate-800 dark:text-white mb-6">
              <TrendingUp className="w-5 h-5 text-purple-500" />
              <h3 className="font-semibold text-lg">Top Skills Trajectory (Emerging Trends)</h3>
            </div>
            <div className="h-80">
              {skillTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={skillTrends} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}/>
                    <Legend />
                    {trendKeys.map((key, index) => (
                      <Line 
                        key={key} 
                        type="monotone" 
                        dataKey={key} 
                        stroke={colors[index % colors.length]} 
                        strokeWidth={3}
                        dot={{ r: 4, strokeWidth: 2 }}
                        activeDot={{ r: 6 }} 
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-slate-400">
                  Not enough time-series data yet.
                </div>
              )}
            </div>
          </div>

          {/* Top Skills Table */}
          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col">
            <div className="flex items-center gap-3 text-slate-800 dark:text-white mb-4">
              <Layers className="w-5 h-5 text-orange-500" />
              <h3 className="font-semibold text-lg">Highest Demand Skills</h3>
            </div>
            <div className="flex-1 overflow-y-auto pr-2">
              <div className="space-y-3">
                {demandSkills.map((skill: any, idx: number) => (
                  <div key={skill.skill_id} className="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-slate-100 dark:border-slate-800">
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400 font-mono text-sm">#{idx + 1}</span>
                      <div>
                        <p className="font-medium text-sm text-slate-900 dark:text-white">{skill.skill_name}</p>
                        <p className="text-xs text-slate-500">{skill.category || 'General'}</p>
                      </div>
                    </div>
                    <span className="bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 px-2 py-1 rounded text-xs font-semibold">
                      {skill.demand_count}
                    </span>
                  </div>
                ))}
                {demandSkills.length === 0 && <p className="text-slate-400 text-sm">No skills tracked.</p>}
              </div>
            </div>
          </div>
        </div>

      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Header & Tabs */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Labour Market</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">Manage data pipelines and view aggregated intelligence.</p>
        </div>
        
        <div className="flex bg-slate-100 dark:bg-slate-900 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('gap')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'gap' 
                ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            Gap Analysis
          </button>
          <button
            onClick={() => setActiveTab('intelligence')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'intelligence' 
                ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            Market Intelligence
          </button>
          <button
            onClick={() => setActiveTab('pipeline')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'pipeline' 
                ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            Pipeline Operations
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="min-h-[600px]">
        {activeTab === 'gap' && renderGapEngine()}
        {activeTab === 'intelligence' && renderIntelligence()}
        {activeTab === 'pipeline' && renderPipeline()}
      </div>

    </div>
  )
}
