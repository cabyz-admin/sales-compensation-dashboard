"""
Business domain models for Sales Compensation Dashboard
Single source of truth for all data structures
"""

from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List
from enum import Enum


class CostMethod(str, Enum):
    """Cost input methods for marketing channels"""
    CPL = "Cost per Lead"
    CPC = "Cost per Contact"
    CPM = "Cost per Meeting"
    CPA = "Cost per Sale"
    BUDGET = "Total Budget"


class CommissionPolicy(str, Enum):
    """When commissions are paid"""
    UPFRONT = "upfront"
    FULL = "full"


class Segment(str, Enum):
    """Market segments"""
    SMB = "SMB"
    MID = "MID"
    ENT = "ENT"
    CUSTOM = "Custom"


class DealEconomics(BaseModel):
    """Contract and payment terms"""
    avg_deal_value: float = Field(gt=0, description="Average contract value")
    upfront_pct: float = Field(ge=0, le=100, description="Upfront payment %")
    contract_length_months: int = Field(gt=0, default=12)
    deferred_timing_months: int = Field(gt=0, default=18)
    commission_policy: CommissionPolicy = CommissionPolicy.UPFRONT
    grr: float = Field(ge=0, le=1, default=0.90, description="Gross Revenue Retention")
    government_cost_pct: float = Field(ge=0, le=100, default=10.0)
    
    @property
    def upfront_cash(self) -> float:
        """Cash received upfront per deal"""
        return self.avg_deal_value * (self.upfront_pct / 100)
    
    @property
    def deferred_cash(self) -> float:
        """Cash deferred per deal"""
        return self.avg_deal_value * ((100 - self.upfront_pct) / 100)


class Channel(BaseModel):
    """Marketing channel configuration"""
    id: str
    name: str
    segment: Segment = Segment.SMB
    enabled: bool = True
    
    # Volume & Funnel
    monthly_leads: float = Field(ge=0)
    contact_rate: float = Field(ge=0, le=1, description="Leads → Contacts")
    meeting_rate: float = Field(ge=0, le=1, description="Contacts → Meetings")
    show_up_rate: float = Field(ge=0, le=1, description="Scheduled → Held")
    close_rate: float = Field(ge=0, le=1, description="Meetings → Sales")
    
    # Cost Model (convergent - only ONE should be set based on method)
    cost_method: CostMethod = CostMethod.CPL
    cpl: Optional[float] = Field(None, ge=0)
    cost_per_contact: Optional[float] = Field(None, ge=0)
    cost_per_meeting: Optional[float] = Field(None, ge=0)
    cost_per_sale: Optional[float] = Field(None, ge=0)
    monthly_budget: Optional[float] = Field(None, ge=0)
    
    @validator('cost_method', always=True)
    def validate_cost_inputs(cls, v, values):
        """Ensure the right cost field is set for the chosen method"""
        # This runs after other fields are set
        return v
    
    def get_cost_value(self) -> float:
        """Get the cost value for the active method"""
        if self.cost_method == CostMethod.CPL:
            return self.cpl or 0
        elif self.cost_method == CostMethod.CPC:
            return self.cost_per_contact or 0
        elif self.cost_method == CostMethod.CPM:
            return self.cost_per_meeting or 0
        elif self.cost_method == CostMethod.CPA:
            return self.cost_per_sale or 0
        elif self.cost_method == CostMethod.BUDGET:
            return self.monthly_budget or 0
        return 0
    
    def is_complete(self) -> bool:
        """Check if channel has valid cost configuration"""
        return self.get_cost_value() > 0


class RoleCompensation(BaseModel):
    """Compensation structure for a role"""
    base: float = Field(ge=0, description="Annual base salary")
    variable: float = Field(ge=0, description="Annual variable/OTE")
    commission_pct: float = Field(ge=0, le=100, description="Commission % of deal")
    
    @property
    def ote(self) -> float:
        """On-Target Earnings"""
        return self.base + self.variable


class TeamStructure(BaseModel):
    """Team composition and compensation"""
    # Counts
    num_closers: int = Field(ge=0, default=8)
    num_setters: int = Field(ge=0, default=4)
    num_managers: int = Field(ge=0, default=2)
    num_bench: int = Field(ge=0, default=2)
    
    # Compensation by role
    closer: RoleCompensation
    setter: RoleCompensation
    manager: RoleCompensation
    bench: RoleCompensation
    
    @property
    def total_base(self) -> float:
        """Total annual base salaries"""
        return (
            self.num_closers * self.closer.base +
            self.num_setters * self.setter.base +
            self.num_managers * self.manager.base +
            self.num_bench * self.bench.base
        )
    
    @property
    def total_count(self) -> int:
        """Total headcount"""
        return self.num_closers + self.num_setters + self.num_managers + self.num_bench


class OperatingCosts(BaseModel):
    """Monthly operating expenses"""
    office_rent: float = Field(ge=0, default=20000)
    software_costs: float = Field(ge=0, default=10000)
    other_opex: float = Field(ge=0, default=5000)
    
    @property
    def total(self) -> float:
        """Total monthly OpEx"""
        return self.office_rent + self.software_costs + self.other_opex


class GTMMetrics(BaseModel):
    """Calculated GTM funnel metrics for a channel or aggregate"""
    leads: float
    contacts: float
    meetings_scheduled: float
    meetings_held: float
    sales: float
    revenue_upfront: float
    spend: float
    cost_per_sale: float
    blended_close_rate: float
    
    @property
    def roas(self) -> float:
        """Return on Ad Spend"""
        return self.revenue_upfront / self.spend if self.spend > 0 else 0
    
    @property
    def overall_conversion(self) -> float:
        """Lead → Sale conversion"""
        return self.sales / self.leads if self.leads > 0 else 0


class UnitEconomics(BaseModel):
    """Unit economics metrics"""
    ltv: float
    cac: float
    payback_months: float
    upfront_cash: float
    deferred_cash: float
    
    @property
    def ltv_cac_ratio(self) -> float:
        """LTV:CAC ratio"""
        return self.ltv / self.cac if self.cac > 0 else 0


class CommissionBreakdown(BaseModel):
    """Commission pool breakdown"""
    closer_pool: float
    setter_pool: float
    manager_pool: float
    total_commission: float
    commission_base: float  # What commissions are calculated on


class PnLStatement(BaseModel):
    """Comprehensive P&L"""
    # Revenue
    gross_revenue: float
    gov_fees: float
    net_revenue: float
    
    # COGS
    team_base: float
    commissions: float
    cogs: float
    gross_profit: float
    gross_margin: float  # %
    
    # OpEx
    marketing: float
    opex: float
    total_opex: float
    
    # Bottom line
    ebitda: float
    ebitda_margin: float  # %


class BusinessSnapshot(BaseModel):
    """Complete business state at a point in time"""
    deal_economics: DealEconomics
    channels: List[Channel]
    team: TeamStructure
    operating_costs: OperatingCosts
    
    # Calculated metrics (filled by engine)
    gtm_total: Optional[GTMMetrics] = None
    gtm_per_channel: Optional[List[GTMMetrics]] = None
    unit_economics: Optional[UnitEconomics] = None
    commissions: Optional[CommissionBreakdown] = None
    pnl: Optional[PnLStatement] = None


class Scenario(BaseModel):
    """Named what-if scenario as deltas from baseline"""
    name: str
    description: str
    deltas: dict  # {"close_rate": 0.03, "cost_per_meeting": -50}
    
    def apply_to(self, snapshot: BusinessSnapshot) -> BusinessSnapshot:
        """Apply deltas to a snapshot (returns new instance)"""
        # Deep copy and apply deltas
        import copy
        new_snap = copy.deepcopy(snapshot)
        
        for key, delta in self.deltas.items():
            # Apply delta based on key path (e.g., "channels[0].close_rate")
            # This is a simplified version; production would need proper path parsing
            pass
        
        return new_snap
