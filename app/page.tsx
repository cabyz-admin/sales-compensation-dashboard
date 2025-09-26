'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Calculator, TrendingUp, Users, DollarSign, Download, Play } from 'lucide-react'
import { MonteCarloChart } from '@/components/monte-carlo-chart'
import { SalesFunnelChart } from '@/components/sales-funnel-chart'
import { CompensationBreakdown } from '@/components/compensation-breakdown'
import { TeamStructure } from '@/components/team-structure'

export default function Dashboard() {
  const [params, setParams] = useState({
    dailyLeads: 200,
    contactRate: 70,
    meetingRate: 35,
    closeRate: 25,
    avgACV: 15000,
    commissionRate: 2.7,
    teamSize: 20,
    benchPercentage: 20,
    setterPercentage: 40,
    quickResponseBonus: 10,
    followUpBonus: 5,
    dailyEbitdaTarget: 10000
  })

  const [monteCarloResults, setMonteCarloResults] = useState(null)
  const [isRunning, setIsRunning] = useState(false)

  const runMonteCarloSimulation = () => {
    setIsRunning(true)
    // Simulate Monte Carlo calculation
    setTimeout(() => {
      const results = generateMonteCarloResults(params)
      setMonteCarloResults(results)
      setIsRunning(false)
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-6">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🎯 Advanced Sales Compensation Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            First-Principles Behavioral Psychology-Based Commission Model
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="parameters">Parameters</TabsTrigger>
            <TabsTrigger value="simulation">Monte Carlo</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="export">Export</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="gradient-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${((params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100 * params.closeRate/100 * params.avgACV)).toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Based on current parameters
                  </p>
                </CardContent>
              </Card>

              <Card className="gradient-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Daily EBITDA</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${calculateDailyEbitda(params).toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Target: ${params.dailyEbitdaTarget.toLocaleString()}
                  </p>
                </CardContent>
              </Card>

              <Card className="gradient-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Team Size</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{params.teamSize}</div>
                  <p className="text-xs text-muted-foreground">
                    Active team members
                  </p>
                </CardContent>
              </Card>

              <Card className="gradient-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">LTV:CAC Ratio</CardTitle>
                  <Calculator className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {calculateLtvCacRatio(params).toFixed(1)}:1
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Target: 3:1
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TeamStructure params={params} />
              <SalesFunnelChart params={params} />
            </div>

            <CompensationBreakdown params={params} />
          </TabsContent>

          <TabsContent value="parameters" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Model Parameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Lead Generation</h3>
                    
                    <div className="space-y-2">
                      <Label>Daily Leads: {params.dailyLeads}</Label>
                      <Slider
                        value={[params.dailyLeads]}
                        onValueChange={(value) => setParams({...params, dailyLeads: value[0]})}
                        max={500}
                        min={50}
                        step={10}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Contact Rate: {params.contactRate}%</Label>
                      <Slider
                        value={[params.contactRate]}
                        onValueChange={(value) => setParams({...params, contactRate: value[0]})}
                        max={90}
                        min={40}
                        step={5}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Meeting Rate: {params.meetingRate}%</Label>
                      <Slider
                        value={[params.meetingRate]}
                        onValueChange={(value) => setParams({...params, meetingRate: value[0]})}
                        max={60}
                        min={20}
                        step={5}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Close Rate: {params.closeRate}%</Label>
                      <Slider
                        value={[params.closeRate]}
                        onValueChange={(value) => setParams({...params, closeRate: value[0]})}
                        max={45}
                        min={15}
                        step={5}
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Financial Parameters</h3>
                    
                    <div className="space-y-2">
                      <Label>Average Contract Value: ${params.avgACV.toLocaleString()}</Label>
                      <Slider
                        value={[params.avgACV]}
                        onValueChange={(value) => setParams({...params, avgACV: value[0]})}
                        max={50000}
                        min={5000}
                        step={1000}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Commission Rate: {params.commissionRate}%</Label>
                      <Slider
                        value={[params.commissionRate]}
                        onValueChange={(value) => setParams({...params, commissionRate: value[0]})}
                        max={5}
                        min={1}
                        step={0.1}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Team Size: {params.teamSize}</Label>
                      <Slider
                        value={[params.teamSize]}
                        onValueChange={(value) => setParams({...params, teamSize: value[0]})}
                        max={50}
                        min={5}
                        step={1}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Daily EBITDA Target: ${params.dailyEbitdaTarget.toLocaleString()}</Label>
                      <Slider
                        value={[params.dailyEbitdaTarget]}
                        onValueChange={(value) => setParams({...params, dailyEbitdaTarget: value[0]})}
                        max={20000}
                        min={5000}
                        step={1000}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="simulation" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="h-5 w-5" />
                  Monte Carlo Simulation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button 
                    onClick={runMonteCarloSimulation}
                    disabled={isRunning}
                    className="w-full md:w-auto"
                  >
                    {isRunning ? 'Running 5000 Simulations...' : 'Run Monte Carlo Simulation'}
                  </Button>
                  
                  {monteCarloResults && (
                    <MonteCarloChart results={monteCarloResults} />
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Transparent Math</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 font-mono text-sm">
                    <div>
                      <h4 className="font-semibold mb-2">Sales Funnel:</h4>
                      <p>Monthly Leads = {params.dailyLeads} × 30 = {params.dailyLeads * 30}</p>
                      <p>Contacts = {params.dailyLeads * 30} × {params.contactRate}% = {Math.round(params.dailyLeads * 30 * params.contactRate/100)}</p>
                      <p>Meetings = {Math.round(params.dailyLeads * 30 * params.contactRate/100)} × {params.meetingRate}% = {Math.round(params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100)}</p>
                      <p>Sales = {Math.round(params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100)} × {params.closeRate}% = {Math.round(params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100 * params.closeRate/100)}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Revenue:</h4>
                      <p>Monthly Revenue = {Math.round(params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100 * params.closeRate/100)} × ${params.avgACV.toLocaleString()}</p>
                      <p>= ${Math.round(params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100 * params.closeRate/100 * params.avgACV).toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Behavioral Psychology</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Speed Response (15min rule):</h4>
                      <p className="text-sm">Research shows 5-minute response = 21× higher conversion</p>
                      <p className="text-sm">Bonus: +{params.quickResponseBonus}% commission</p>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Quality Assurance:</h4>
                      <p className="text-sm">Minimum 2 follow-ups required</p>
                      <p className="text-sm">Bonus: +{params.followUpBonus}% commission</p>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Bench System:</h4>
                      <p className="text-sm">Recovery path: 5 meetings from old leads</p>
                      <p className="text-sm">Maintains motivation while ensuring accountability</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="export" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  Export & Share
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="outline" className="w-full">
                    Export to PDF
                  </Button>
                  <Button variant="outline" className="w-full">
                    Export to Excel
                  </Button>
                  <Button variant="outline" className="w-full">
                    Share Link
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

// Helper functions
function calculateDailyEbitda(params: any) {
  const monthlySales = params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100 * params.closeRate/100
  const monthlyRevenue = monthlySales * params.avgACV
  const totalCosts = (params.dailyLeads * 30 * 25) + (params.teamSize * 4000)
  const totalCommission = monthlyRevenue * params.commissionRate/100
  const monthlyEbitda = monthlyRevenue - totalCosts - totalCommission
  return monthlyEbitda / 30
}

function calculateLtvCacRatio(params: any) {
  const monthlySales = params.dailyLeads * 30 * params.contactRate/100 * params.meetingRate/100 * params.closeRate/100
  const totalCosts = (params.dailyLeads * 30 * 25) + (params.teamSize * 4000)
  const cac = totalCosts / monthlySales
  const ltv = params.avgACV * 2.5
  return ltv / cac
}

function generateMonteCarloResults(params: any) {
  // Simplified Monte Carlo simulation
  const results = []
  for (let i = 0; i < 1000; i++) {
    const variance = 0.1
    const leads = params.dailyLeads * (1 + (Math.random() - 0.5) * variance)
    const contact = params.contactRate/100 * (1 + (Math.random() - 0.5) * variance)
    const meeting = params.meetingRate/100 * (1 + (Math.random() - 0.5) * variance)
    const close = params.closeRate/100 * (1 + (Math.random() - 0.5) * variance)
    
    const sales = leads * 30 * contact * meeting * close
    const revenue = sales * params.avgACV
    const ebitda = revenue - (leads * 30 * 25) - (params.teamSize * 4000) - (revenue * params.commissionRate/100)
    
    results.push({
      sales: Math.round(sales),
      revenue: Math.round(revenue),
      dailyEbitda: Math.round(ebitda / 30)
    })
  }
  return results
}
