import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Search, Users, Target, BookOpen, ChevronRight } from 'lucide-react'
import { getStudents, type StudentListItem } from '../../../api/endpoints/professors'
import { Card, Spinner, Badge } from '../../../components/ui'

export function ProfessorStudentList() {
  const [students, setStudents] = useState<StudentListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [branch, setBranch] = useState('')
  const [year, setYear] = useState('')
  const [order, setOrder] = useState('-date_joined')

  const fetchStudents = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getStudents({ search, branch, year, order })
      setStudents(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load students')
    } finally {
      setLoading(false)
    }
  }, [search, branch, year, order])

  useEffect(() => {
    const timer = setTimeout(fetchStudents, 300)
    return () => clearTimeout(timer)
  }, [fetchStudents])

  const uniqueBranches = [...new Set(students.map(s => s.branch).filter(Boolean))]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Students</h2>
        <p className="mt-1 text-sm text-slate-500">
          View and manage your students' career profiles and progress.
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by name, email, or college..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <select
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Branches</option>
              {uniqueBranches.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>

            <select
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Years</option>
              <option value="1">Year 1</option>
              <option value="2">Year 2</option>
              <option value="3">Year 3</option>
              <option value="4">Year 4</option>
            </select>

            <select
              value={order}
              onChange={(e) => setOrder(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
            >
              <option value="-date_joined">Newest First</option>
              <option value="date_joined">Oldest First</option>
              <option value="first_name">Name A-Z</option>
              <option value="-first_name">Name Z-A</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Results count */}
      {!loading && (
        <p className="text-sm text-slate-500">
          {students.length} student{students.length !== 1 ? 's' : ''} found
        </p>
      )}

      {loading && <Spinner />}
      {error && <div className="text-red-600 text-sm">{error}</div>}

      {/* Student cards */}
      {!loading && !error && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {students.map((student) => (
            <Link
              key={student.id}
              to={`/professor/students/${student.id}`}
              className="block"
            >
              <Card className="hover:border-brand-300 hover:shadow-md transition-all cursor-pointer h-full">
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <h3 className="font-medium text-slate-900 truncate">
                      {student.full_name}
                    </h3>
                    <p className="text-sm text-slate-500 truncate">{student.email}</p>
                  </div>
                  <ChevronRight className="h-5 w-5 text-slate-400 shrink-0" />
                </div>

                <div className="mt-3 space-y-2 text-sm">
                  {student.college && (
                    <p className="text-slate-600 truncate">{student.college}</p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {student.course && (
                      <Badge>{student.course}</Badge>
                    )}
                    {student.branch && (
                      <Badge>{student.branch}</Badge>
                    )}
                    {student.year && (
                      <Badge tone="slate">Year {student.year}</Badge>
                    )}
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <Target className="h-4 w-4 mx-auto text-brand-600" />
                    <p className="mt-1 font-medium text-slate-900">
                      {student.career_readiness}%
                    </p>
                    <p className="text-slate-500">Readiness</p>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <BookOpen className="h-4 w-4 mx-auto text-emerald-600" />
                    <p className="mt-1 font-medium text-slate-900">
                      {student.skills_count}
                    </p>
                    <p className="text-slate-500">Skills</p>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <Users className="h-4 w-4 mx-auto text-amber-600" />
                    <p className="mt-1 font-medium text-slate-900">
                      {student.profile_completeness}%
                    </p>
                    <p className="text-slate-500">Profile</p>
                  </div>
                </div>
              </Card>
            </Link>
          ))}

          {students.length === 0 && (
            <div className="col-span-full text-center py-12 text-slate-500">
              No students found matching your criteria.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
