from typing import List, Dict, Any
from .context import SearchContext, AgentType

class FilterSortAgent:
    """
    Filters and sorts layout approvals based on criteria
    """
    
    MIN_AREA_ACRES = 5.0  # Minimum approved land area
    
    async def filter_and_sort(self, context: SearchContext) -> SearchContext:
        """
        Filter layout approvals and sort by approval date (descending)
        """
        
        try:
            filtered = context.layout_approvals.copy()
            
            # Filter by minimum area (> 5 acres)
            filtered = [a for a in filtered if a.get("approved_area", 0) >= self.MIN_AREA_ACRES]
            
            # Sort by approval date (descending - most recent first)
            filtered.sort(
                key=lambda x: x.get("approval_date", ""),
                reverse=True
            )
            
            context.filtered_approvals = filtered
            
            context.add_workflow_step(
                AgentType.FILTER,
                "success",
                {
                    "initial_count": len(context.layout_approvals),
                    "filtered_count": len(filtered),
                    "min_area_filter": f"{self.MIN_AREA_ACRES} acres",
                    "sort_by": "approval_date (descending)"
                }
            )
            
        except Exception as e:
            context.add_workflow_step(
                AgentType.FILTER,
                "failed",
                {"approvals_count": len(context.layout_approvals)},
                str(e)
            )
        
        return context
