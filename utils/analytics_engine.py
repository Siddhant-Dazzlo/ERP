import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from flask import current_app

class AnalyticsEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.cache = {}
        try:
            self.cache_duration = current_app.config.get('ANALYTICS_CACHE_DURATION', 300)
        except RuntimeError:
            self.cache_duration = 300  # Default value when outside app context
    
    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics with advanced metrics"""
        cache_key = 'comprehensive_analytics'
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        analytics = {
            'overview': self._get_overview_metrics(),
            'financial': self._get_financial_analytics(),
            'operational': self._get_operational_analytics(),
            'performance': self._get_performance_analytics(),
            'trends': self._get_trend_analytics(),
            'predictions': self._get_predictive_analytics(),
            'charts': self._generate_charts()
        }
        
        self._cache_data(cache_key, analytics)
        return analytics
    
    def _get_overview_metrics(self) -> Dict[str, Any]:
        """Get high-level overview metrics"""
        projects = self.data_manager.get_all_projects()
        users = self.data_manager.get_all_users()
        clients = self.data_manager.get_all_clients()
        leads = self.data_manager.get_all_leads()
        
        # Calculate key metrics
        total_revenue = sum(p.get('budget', 0) for p in projects)
        active_projects = len([p for p in projects if p.get('status') == 'in_progress'])
        completed_projects = len([p for p in projects if p.get('status') == 'completed'])
        conversion_rate = self._calculate_lead_conversion_rate()
        
        return {
            'total_projects': len(projects),
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_revenue': total_revenue,
            'total_clients': len(clients),
            'total_leads': len(leads),
            'conversion_rate': conversion_rate,
            'active_employees': len([u for u in users if u.get('role') == 'employee' and u.get('status') == 'active']),
            'project_completion_rate': (completed_projects / len(projects) * 100) if projects else 0
        }
    
    def _get_financial_analytics(self) -> Dict[str, Any]:
        """Get detailed financial analytics"""
        projects = self.data_manager.get_all_projects()
        
        # Revenue analysis by type
        installation_revenue = sum(p.get('budget', 0) for p in projects if p.get('type') == 'installation')
        manufacturing_revenue = sum(p.get('budget', 0) for p in projects if p.get('type') == 'manufacturing')
        
        # Monthly revenue trends
        monthly_revenue = self._calculate_monthly_revenue()
        
        # Profitability analysis (assuming 30% profit margin)
        total_cost = sum(p.get('budget', 0) * 0.7 for p in projects)
        total_profit = sum(p.get('budget', 0) * 0.3 for p in projects)
        
        return {
            'total_revenue': sum(p.get('budget', 0) for p in projects),
            'installation_revenue': installation_revenue,
            'manufacturing_revenue': manufacturing_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'profit_margin': (total_profit / (total_cost + total_profit) * 100) if (total_cost + total_profit) > 0 else 0,
            'monthly_revenue': monthly_revenue,
            'average_project_value': sum(p.get('budget', 0) for p in projects) / len(projects) if projects else 0
        }
    
    def _get_operational_analytics(self) -> Dict[str, Any]:
        """Get operational efficiency metrics"""
        projects = self.data_manager.get_all_projects()
        attendance_records = self.data_manager.data.get('attendance', [])
        
        # Project efficiency
        project_durations = []
        for project in projects:
            if project.get('start_date') and project.get('end_date'):
                start = datetime.strptime(project['start_date'], '%Y-%m-%d')
                end = datetime.strptime(project['end_date'], '%Y-%m-%d')
                duration = (end - start).days
                project_durations.append(duration)
        
        avg_project_duration = np.mean(project_durations) if project_durations else 0
        
        # Attendance analysis
        today = datetime.now().strftime('%Y-%m-%d')
        today_attendance = len([r for r in attendance_records if r.get('date') == today])
        total_employees = len([u for u in self.data_manager.get_all_users() if u.get('role') == 'employee'])
        attendance_rate = (today_attendance / total_employees * 100) if total_employees > 0 else 0
        
        return {
            'average_project_duration': avg_project_duration,
            'attendance_rate': attendance_rate,
            'total_attendance_records': len(attendance_records),
            'projects_on_time': len([p for p in projects if p.get('status') == 'completed']),
            'projects_delayed': len([p for p in projects if p.get('status') == 'in_progress' and 
                                   p.get('end_date') and datetime.strptime(p['end_date'], '%Y-%m-%d') < datetime.now()])
        }
    
    def _get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance and productivity metrics"""
        projects = self.data_manager.get_all_projects()
        users = self.data_manager.get_all_users()
        
        # Employee performance
        employee_performance = {}
        for user in users:
            if user.get('role') == 'employee':
                assigned_projects = [p for p in projects if user['id'] in p.get('assigned_employees', [])]
                completed_projects = [p for p in assigned_projects if p.get('status') == 'completed']
                
                employee_performance[user['id']] = {
                    'name': user['name'],
                    'total_projects': len(assigned_projects),
                    'completed_projects': len(completed_projects),
                    'completion_rate': (len(completed_projects) / len(assigned_projects) * 100) if assigned_projects else 0,
                    'total_revenue': sum(p.get('budget', 0) for p in assigned_projects)
                }
        
        # Department performance
        department_stats = defaultdict(lambda: {'projects': 0, 'revenue': 0, 'employees': 0})
        for user in users:
            if user.get('role') == 'employee':
                dept = user.get('department', 'General')
                department_stats[dept]['employees'] += 1
                
                assigned_projects = [p for p in projects if user['id'] in p.get('assigned_employees', [])]
                department_stats[dept]['projects'] += len(assigned_projects)
                department_stats[dept]['revenue'] += sum(p.get('budget', 0) for p in assigned_projects)
        
        return {
            'employee_performance': employee_performance,
            'department_performance': dict(department_stats),
            'top_performers': sorted(employee_performance.values(), 
                                   key=lambda x: x['completion_rate'], reverse=True)[:5]
        }
    
    def _get_trend_analytics(self) -> Dict[str, Any]:
        """Get trend analysis over time"""
        projects = self.data_manager.get_all_projects()
        leads = self.data_manager.get_all_leads()
        
        # Monthly trends
        monthly_data = defaultdict(lambda: {'projects': 0, 'revenue': 0, 'leads': 0})
        
        for project in projects:
            if project.get('created_at'):
                month = project['created_at'][:7]  # YYYY-MM
                monthly_data[month]['projects'] += 1
                monthly_data[month]['revenue'] += project.get('budget', 0)
        
        for lead in leads:
            if lead.get('created_at'):
                month = lead['created_at'][:7]
                monthly_data[month]['leads'] += 1
        
        # Convert to sorted list
        monthly_trends = sorted(monthly_data.items())
        
        return {
            'monthly_trends': monthly_trends,
            'growth_rate': self._calculate_growth_rate(monthly_trends),
            'seasonal_patterns': self._identify_seasonal_patterns(monthly_trends)
        }
    
    def _get_predictive_analytics(self) -> Dict[str, Any]:
        """Get predictive analytics and forecasts"""
        projects = self.data_manager.get_all_projects()
        leads = self.data_manager.get_all_leads()
        
        # Simple forecasting based on historical data
        if len(projects) > 0:
            recent_projects = sorted(projects, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
            avg_monthly_projects = len(recent_projects) / 3  # Assuming 3 months of data
            
            # Revenue forecast
            avg_project_value = sum(p.get('budget', 0) for p in projects) / len(projects)
            projected_revenue = avg_monthly_projects * avg_project_value * 12
        else:
            projected_revenue = 0
            avg_monthly_projects = 0
        
        return {
            'projected_annual_revenue': projected_revenue,
            'projected_monthly_projects': avg_monthly_projects,
            'lead_conversion_forecast': self._forecast_lead_conversion(),
            'resource_requirements': self._forecast_resource_needs()
        }
    
    def _generate_charts(self) -> Dict[str, str]:
        """Generate chart images as base64 strings"""
        charts = {}
        
        try:
            # Revenue by type chart
            projects = self.data_manager.get_all_projects()
            revenue_by_type = {
                'Installation': sum(p.get('budget', 0) for p in projects if p.get('type') == 'installation'),
                'Manufacturing': sum(p.get('budget', 0) for p in projects if p.get('type') == 'manufacturing')
            }
            
            plt.figure(figsize=(10, 6))
            plt.pie(revenue_by_type.values(), labels=revenue_by_type.keys(), autopct='%1.1f%%')
            plt.title('Revenue Distribution by Project Type')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            charts['revenue_distribution'] = f"data:image/png;base64,{chart_data}"
            plt.close()
            
            # Monthly trends chart
            monthly_data = self._get_monthly_data_for_chart()
            if monthly_data:
                plt.figure(figsize=(12, 6))
                months = list(monthly_data.keys())
                revenues = list(monthly_data.values())
                
                plt.plot(months, revenues, marker='o', linewidth=2, markersize=6)
                plt.title('Monthly Revenue Trends')
                plt.xlabel('Month')
                plt.ylabel('Revenue ($)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                chart_data = base64.b64encode(buffer.getvalue()).decode()
                charts['monthly_trends'] = f"data:image/png;base64,{chart_data}"
                plt.close()
            
        except Exception as e:
            current_app.logger.error(f"Failed to generate charts: {str(e)}")
        
        return charts
    
    def _calculate_lead_conversion_rate(self) -> float:
        """Calculate lead conversion rate"""
        leads = self.data_manager.get_all_leads()
        if not leads:
            return 0
        
        converted_leads = len([l for l in leads if l.get('status') == 'converted'])
        return (converted_leads / len(leads)) * 100
    
    def _calculate_monthly_revenue(self) -> Dict[str, float]:
        """Calculate monthly revenue for the last 12 months"""
        projects = self.data_manager.get_all_projects()
        monthly_revenue = defaultdict(float)
        
        for project in projects:
            if project.get('created_at'):
                month = project['created_at'][:7]  # YYYY-MM
                monthly_revenue[month] += project.get('budget', 0)
        
        return dict(monthly_revenue)
    
    def _calculate_growth_rate(self, monthly_trends: List[Tuple[str, Dict]]) -> float:
        """Calculate growth rate from monthly trends"""
        if len(monthly_trends) < 2:
            return 0
        
        recent = monthly_trends[-1][1]['revenue']
        previous = monthly_trends[-2][1]['revenue']
        
        if previous == 0:
            return 0
        
        return ((recent - previous) / previous) * 100
    
    def _identify_seasonal_patterns(self, monthly_trends: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Identify seasonal patterns in data"""
        if len(monthly_trends) < 12:
            return {'has_patterns': False, 'message': 'Insufficient data for seasonal analysis'}
        
        revenues = [data['revenue'] for _, data in monthly_trends]
        
        # Simple seasonal analysis
        avg_revenue = np.mean(revenues)
        std_revenue = np.std(revenues)
        
        return {
            'has_patterns': std_revenue > avg_revenue * 0.2,  # 20% variation threshold
            'average_revenue': avg_revenue,
            'volatility': std_revenue / avg_revenue if avg_revenue > 0 else 0
        }
    
    def _forecast_lead_conversion(self) -> Dict[str, float]:
        """Forecast lead conversion rates"""
        leads = self.data_manager.get_all_leads()
        if not leads:
            return {'conversion_rate': 0, 'confidence': 0}
        
        # Simple forecasting based on recent performance
        recent_leads = sorted(leads, key=lambda x: x.get('created_at', ''), reverse=True)[:20]
        recent_conversions = len([l for l in recent_leads if l.get('status') == 'converted'])
        
        forecast_rate = (recent_conversions / len(recent_leads)) * 100 if recent_leads else 0
        
        return {
            'conversion_rate': forecast_rate,
            'confidence': min(95, max(50, len(recent_leads) * 5))  # Confidence based on sample size
        }
    
    def _forecast_resource_needs(self) -> Dict[str, Any]:
        """Forecast resource requirements"""
        projects = self.data_manager.get_all_projects()
        active_projects = [p for p in projects if p.get('status') == 'in_progress']
        
        total_workload = sum(len(p.get('assigned_employees', [])) for p in active_projects)
        available_employees = len([u for u in self.data_manager.get_all_users() 
                                 if u.get('role') == 'employee' and u.get('status') == 'active'])
        
        utilization_rate = (total_workload / available_employees * 100) if available_employees > 0 else 0
        
        return {
            'current_utilization': utilization_rate,
            'recommended_hiring': 'High' if utilization_rate > 80 else 'Medium' if utilization_rate > 60 else 'Low',
            'estimated_workload': total_workload
        }
    
    def _get_monthly_data_for_chart(self) -> Dict[str, float]:
        """Get monthly data formatted for charting"""
        monthly_revenue = self._calculate_monthly_revenue()
        if not monthly_revenue:
            return {}
        
        # Sort by month and get last 12 months
        sorted_months = sorted(monthly_revenue.keys())[-12:]
        return {month: monthly_revenue[month] for month in sorted_months}
    
    def _get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now().timestamp() - timestamp < self.cache_duration:
                return data
            else:
                del self.cache[key]
        return None
    
    def _cache_data(self, key: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self.cache[key] = (data, datetime.now().timestamp())
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
    
    def generate_custom_report(self, report_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate custom reports based on type and filters"""
        if report_type == 'financial':
            return self._generate_financial_report(filters)
        elif report_type == 'operational':
            return self._generate_operational_report(filters)
        elif report_type == 'performance':
            return self._generate_performance_report(filters)
        else:
            return {'error': 'Unknown report type'}
    
    def _generate_financial_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate detailed financial report"""
        return {
            'report_type': 'financial',
            'generated_at': datetime.now().isoformat(),
            'data': self._get_financial_analytics(),
            'filters_applied': filters or {}
        }
    
    def _generate_operational_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate operational efficiency report"""
        return {
            'report_type': 'operational',
            'generated_at': datetime.now().isoformat(),
            'data': self._get_operational_analytics(),
            'filters_applied': filters or {}
        }
    
    def _generate_performance_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate performance and productivity report"""
        return {
            'report_type': 'performance',
            'generated_at': datetime.now().isoformat(),
            'data': self._get_performance_analytics(),
            'filters_applied': filters or {}
        }
