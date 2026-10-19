import api from './api';

export interface AuditTaskItem {
  id: number;
  task_id: string;
  title: string;
  state: string;
  start_date: string | null;
  start_year: number | null;
  end_date: string | null;
  deadline: string | null;
  dias_restantes: number | null;
  prazo_status: 'Prazo Amplo' | 'Prazo Encerrando' | 'Prazo Venceu' | 'Sem Prazo';
  situation: string | null;
  monitoring_text: string | null;
  action_taken: string | null;
  governance_sigla: string | null;
  governance_nome: string | null;
  responsible_area_id: number | null;
  responsible_area_nome: string | null;
}

export interface GovernanceUnit {
  id: number;
  sigla: string;
  nome: string;
  areas: { id: number; nome: string }[];
}

export interface ResponsibleArea {
  id: number;
  nome: string;
  governance_unit_id: number;
  governance_sigla?: string;
  governance_nome?: string;
}

export interface DashboardMetrics {
  filter: string;
  kpis: {
    total_pendentes: number;
    total_atendidas: number;
    total_ativas: number;
    pendentes_sem_area: number;
  };
  situacao: { situacao: string; quantidade: number }[];
  prazo: { status: string; quantidade: number }[];
  por_ano: { ano: string; quantidade: number }[];
  rna_historico: { mes: string; label: string; quantidade: number }[];
}

export interface TasksListResponse {
  items: AuditTaskItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const auditApi = {
  async getDashboard(sigla?: string): Promise<DashboardMetrics> {
    const params = sigla ? { sigla } : {};
    const res = await api.get<DashboardMetrics>('/api/audit-tasks/dashboard', { params });
    return res.data;
  },

  async getTasks(params: {
    page?: number;
    page_size?: number;
    search?: string;
    sigla?: string;
    situation?: string;
    prazo?: string;
    unassigned?: boolean;
    is_active?: boolean;
  }): Promise<TasksListResponse> {
    const res = await api.get<TasksListResponse>('/api/audit-tasks', { params });
    return res.data;
  },

  async getGovernanceUnits(): Promise<GovernanceUnit[]> {
    const res = await api.get<GovernanceUnit[]>('/api/governance-units');
    return res.data;
  },

  async getResponsibleAreas(sigla?: string): Promise<ResponsibleArea[]> {
    const params = sigla ? { sigla } : {};
    const res = await api.get<ResponsibleArea[]>('/api/responsible-areas', { params });
    return res.data;
  },

  async assignResponsibleArea(taskId: string, responsibleAreaId: number | null): Promise<void> {
    await api.patch(`/api/audit-tasks/${taskId}/responsible-area`, {
      responsible_area_id: responsibleAreaId,
    });
  },

  async uploadEcguFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/api/audit-tasks/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};
