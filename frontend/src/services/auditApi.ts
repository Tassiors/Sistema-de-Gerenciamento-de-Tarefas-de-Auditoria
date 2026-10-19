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
  responsible_area_sigla?: string | null;
  responsible_area_level?: string | null;
  responsible_areas?: { id: number; nome: string; sigla?: string | null; level?: string | null }[];
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
  sigla?: string;
  level?: string;
  parent_id?: number | null;
  governance_unit_id: number;
  governance_sigla?: string;
  governance_nome?: string;
}

export interface SystemManagerItem {
  id: number;
  username: string;
  name: string;
  email: string | null;
  role: 'GESTOR' | 'ADMINISTRADOR' | 'SUPERINTENDENTE' | 'AUDITOR';
  is_active: boolean;
  responsible_area_id: number | null;
  responsible_area_nome: string | null;
  responsible_area_sigla?: string | null;
  responsible_area_level?: string | null;
  responsible_areas?: { id: number; nome: string; sigla?: string | null; level?: string | null }[];
  subordinates_count?: number;
  extra_units: { id: number; nome: string; sigla?: string }[];
  created_at?: string;
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

  async getTaskDetail(taskId: string): Promise<AuditTaskItem> {
    const res = await api.get<AuditTaskItem>(`/api/audit-tasks/${taskId}`);
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

  async assignResponsibleAreas(taskId: string, responsibleAreaIds: number[]): Promise<void> {
    await api.patch(`/api/audit-tasks/${taskId}/responsible-areas`, {
      responsible_area_ids: responsibleAreaIds,
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

  // Matriz de Visibilidade e Gestão de Gestores
  async listManagers(): Promise<SystemManagerItem[]> {
    const res = await api.get<SystemManagerItem[]>('/api/admin/managers');
    return res.data;
  },

  async createManager(data: {
    username: string;
    name: string;
    email?: string;
    role: string;
    responsible_area_id?: number | null;
    is_active?: boolean;
    extra_unit_ids?: number[];
  }): Promise<SystemManagerItem> {
    const res = await api.post<SystemManagerItem>('/api/admin/managers', data);
    return res.data;
  },

  async updateManager(
    id: number,
    data: {
      name?: string;
      email?: string;
      role?: string;
      responsible_area_id?: number | null;
      is_active?: boolean;
      extra_unit_ids?: number[];
    }
  ): Promise<SystemManagerItem> {
    const res = await api.put<SystemManagerItem>(`/api/admin/managers/${id}`, data);
    return res.data;
  },

  async deleteManager(id: number): Promise<void> {
    await api.delete(`/api/admin/managers/${id}`);
  },

  async getSubordinates(areaId: number): Promise<{ area_id: number; subordinate_ids: number[]; count: number }> {
    const res = await api.get(`/api/admin/managers/subordinates/${areaId}`);
    return res.data;
  },
};
