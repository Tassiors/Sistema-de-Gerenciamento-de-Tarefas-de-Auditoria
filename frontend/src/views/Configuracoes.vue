<template>
  <div class="space-y-6">
    <!-- Cabeçalho das Configurações -->
    <Card>
      <template #header>
        <div class="flex items-center space-x-3">
          <Cog6ToothIcon class="h-7 w-7 text-blue-700" />
          <h1 class="text-2xl font-bold text-gray-900">Configurações & Matriz de Visibilidade</h1>
        </div>
      </template>

      <div v-if="authStore.isAdmin" class="space-y-6">
        <p class="text-gray-600 leading-relaxed text-sm">
          Gerencie o acesso ao sistema via Active Directory (AD), pré-cadastro de gestores e a <strong>Matriz de Visibilidade Hierárquica</strong> do organograma HC-UFPE (<strong>Gerência &rarr; Divisão &rarr; Setor &rarr; Unidade</strong>).
        </p>

        <!-- 1. Perfil do Usuário Logado -->
        <div v-if="authStore.user" class="p-5 bg-white border border-gray-200 rounded-xl shadow-xs space-y-3">
          <div class="flex items-center space-x-2 text-gray-900 font-bold text-base border-b border-gray-100 pb-2">
            <UserCircleIcon class="h-5 w-5 text-blue-600" />
            <span>Seu Perfil Corporativo (Active Directory)</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs pt-1">
            <div>
              <p class="text-[10px] font-bold text-gray-400 uppercase">Login AD</p>
              <p class="font-bold text-gray-800 text-sm mt-0.5">{{ authStore.user.username }}</p>
            </div>
            <div>
              <p class="text-[10px] font-bold text-gray-400 uppercase">Nome Completo</p>
              <p class="font-medium text-gray-800 text-sm mt-0.5">{{ authStore.user.displayName?.[0] || authStore.user.username }}</p>
            </div>
            <div>
              <p class="text-[10px] font-bold text-gray-400 uppercase">E-mail</p>
              <p class="font-medium text-gray-800 mt-0.5">{{ authStore.user.email?.[0] || 'Não cadastrado' }}</p>
            </div>
            <div>
              <p class="text-[10px] font-bold text-gray-400 uppercase">Perfil no Sistema</p>
              <p class="font-bold text-blue-700 mt-0.5">ADMINISTRADOR (Acesso Total)</p>
            </div>
          </div>
        </div>

        <!-- 2. Painel de Gestores Autorizados e Matriz de Visibilidade -->
        <div class="p-6 bg-white border border-gray-200 rounded-xl shadow-xs space-y-5">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-gray-100 pb-4 gap-4">
            <div>
              <h2 class="text-base font-bold text-gray-900 flex items-center gap-2">
                <ShieldCheckIcon class="h-5 w-5 text-indigo-600" />
                Gestores Autorizados & Matriz de Visibilidade
              </h2>
              <p class="text-xs text-gray-500 mt-1">
                Apenas gestores pré-cadastrados abaixo conseguem autenticar via AD. A visibilidade de tarefas segue o organograma hierárquico com suporte a unidades extras.
              </p>
            </div>

            <Button variant="primary" @click="openAddManagerModal">
              <template #icon>
                <UserPlusIcon class="h-4 w-4" />
              </template>
              Cadastrar Novo Gestor
            </Button>
          </div>

          <!-- Barra de Busca de Gestores -->
          <div class="flex items-center gap-3">
            <div class="relative flex-1">
              <input
                v-model="managerSearchQuery"
                type="text"
                placeholder="Buscar gestor por nome, login AD, cargo ou unidade..."
                class="w-full text-xs bg-gray-50 border border-gray-300 rounded-lg pl-8 pr-3 py-2 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <MagnifyingGlassIcon class="w-4 h-4 text-gray-400 absolute left-2.5 top-2.5" />
            </div>
            <span class="text-xs text-gray-500 font-semibold whitespace-nowrap">
              {{ filteredManagers.length }} gestores
            </span>
          </div>

          <!-- Tabela de Gestores Cadastrados -->
          <div class="overflow-x-auto border border-gray-200 rounded-xl">
            <table class="w-full text-left text-xs text-gray-700">
              <thead class="bg-gray-50 text-[10px] uppercase font-bold text-gray-500 border-b border-gray-200">
                <tr>
                  <th class="py-3 px-4">Login AD</th>
                  <th class="py-3 px-4">Nome do Colaborador</th>
                  <th class="py-3 px-4">Perfil</th>
                  <th class="py-3 px-4">Unidade Principal</th>
                  <th class="py-3 px-4">Visibilidade Hierárquica</th>
                  <th class="py-3 px-4">Unidades Extras</th>
                  <th class="py-3 px-4 text-center">Status</th>
                  <th class="py-3 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-if="isLoadingManagers">
                  <td colspan="8" class="text-center py-8 text-gray-400 italic">
                    Carregando gestores cadastrados...
                  </td>
                </tr>
                <tr v-else-if="filteredManagers.length === 0">
                  <td colspan="8" class="text-center py-8 text-gray-400 italic">
                    Nenhum gestor encontrado para o termo pesquisado.
                  </td>
                </tr>
                <tr
                  v-for="mgr in filteredManagers"
                  :key="mgr.id"
                  class="hover:bg-blue-50/30 transition-colors"
                >
                  <!-- Login AD -->
                  <td class="py-3 px-4 font-bold text-gray-900 flex items-center gap-2">
                    <UserIcon class="h-3.5 w-3.5 text-gray-400" />
                    {{ mgr.username }}
                  </td>

                  <!-- Nome Completo & Email -->
                  <td class="py-3 px-4">
                    <p class="font-bold text-gray-900">{{ mgr.name }}</p>
                    <p class="text-[10px] text-gray-400">{{ mgr.email || 'Sem e-mail' }}</p>
                  </td>

                  <!-- Perfil -->
                  <td class="py-3 px-4">
                    <span :class="getRoleBadgeClass(mgr.role)" class="px-2 py-0.5 text-[10px] font-bold rounded-md">
                      {{ mgr.role }}
                    </span>
                  </td>

                  <!-- Unidade Principal -->
                  <td class="py-3 px-4">
                    <div v-if="mgr.responsible_area_nome">
                      <span class="font-semibold text-gray-800">{{ mgr.responsible_area_nome }}</span>
                      <span v-if="mgr.responsible_area_sigla" class="text-[10px] text-blue-600 font-bold ml-1">
                        ({{ mgr.responsible_area_sigla }})
                      </span>
                    </div>
                    <span v-else class="text-gray-400 italic">Global (Todas as Áreas)</span>
                  </td>

                  <!-- Visibilidade Hierárquica -->
                  <td class="py-3 px-4">
                    <span
                      v-if="['ADMINISTRADOR', 'SUPERINTENDENTE', 'AUDITOR'].includes(mgr.role)"
                      class="inline-flex items-center gap-1 text-[11px] font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200"
                    >
                      ★ Todas as Tarefas (Irrestrito)
                    </span>
                    <span
                      v-else-if="mgr.subordinates_count && mgr.subordinates_count > 1"
                      class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200"
                    >
                      ✓ +{{ mgr.subordinates_count - 1 }} subordinadas herdadas
                    </span>
                    <span
                      v-else-if="mgr.responsible_area_id"
                      class="text-[11px] text-gray-500"
                    >
                      Apenas unidade própria
                    </span>
                    <span v-else class="text-gray-400 italic">-</span>
                  </td>

                  <!-- Unidades Extras -->
                  <td class="py-3 px-4">
                    <div v-if="mgr.extra_units && mgr.extra_units.length > 0" class="flex flex-wrap gap-1">
                      <span
                        v-for="ex in mgr.extra_units"
                        :key="ex.id"
                        class="px-1.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded text-[10px] font-medium"
                        :title="ex.nome"
                      >
                        {{ ex.sigla || ex.nome }}
                      </span>
                    </div>
                    <span v-else class="text-gray-400 italic text-[11px]">Nenhuma</span>
                  </td>

                  <!-- Status -->
                  <td class="py-3 px-4 text-center">
                    <span
                      :class="mgr.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
                      class="px-2 py-0.5 text-[10px] font-bold rounded-full"
                    >
                      {{ mgr.is_active ? 'ATIVO' : 'INATIVO' }}
                    </span>
                  </td>

                  <!-- Ações -->
                  <td class="py-3 px-4 text-right space-x-2 whitespace-nowrap">
                    <button
                      type="button"
                      @click="openEditManagerModal(mgr)"
                      class="px-2.5 py-1 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition cursor-pointer"
                    >
                      Editar Matriz
                    </button>
                    <button
                      v-if="!['tassio.silva', 'renata.albuquerque.1', 'admin'].includes(mgr.username)"
                      type="button"
                      @click="confirmDeleteManager(mgr)"
                      class="px-2 py-1 text-xs font-semibold text-rose-600 hover:text-rose-800 hover:bg-rose-50 rounded-md transition cursor-pointer"
                      title="Excluir gestor"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Aviso para não administradores -->
      <div v-else class="p-8 text-center text-gray-500 space-y-2">
        <ShieldCheckIcon class="w-12 h-12 text-gray-300 mx-auto" />
        <h3 class="font-bold text-gray-800 text-base">Acesso Restrito</h3>
        <p class="text-xs">Apenas usuários com perfil de Administrador têm permissão para acessar esta tela.</p>
      </div>
    </Card>

    <!-- Modal de Cadastro / Edição de Gestor & Matriz de Visibilidade -->
    <Modal
      :isOpen="showManagerModal"
      :title="editingManagerId ? 'Editar Gestor & Matriz de Visibilidade' : 'Cadastrar Novo Gestor Autorizado'"
      @close="closeManagerModal"
    >
      <div class="space-y-4 text-xs">
        <!-- 1. Login Active Directory -->
        <div>
          <label class="block font-bold text-gray-700 mb-1">
            Login Active Directory (AD) <span class="text-rose-500">*</span>
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model="managerForm.username"
              type="text"
              :disabled="!!editingManagerId"
              placeholder="ex: tassio.silva ou joao.silva"
              class="w-full text-xs border border-gray-300 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
            />
            <Button
              v-if="!editingManagerId"
              type="button"
              variant="secondary"
              @click="searchAD"
              :loading="isSearchingAD"
            >
              Consultar AD
            </Button>
          </div>
          <p v-if="adSearchFeedback" class="text-[11px] font-semibold mt-1" :class="adSearchSuccess ? 'text-emerald-600' : 'text-rose-600'">
            {{ adSearchFeedback }}
          </p>
        </div>

        <!-- 2. Nome Completo e E-mail -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-gray-700 mb-1">
              Nome Completo <span class="text-rose-500">*</span>
            </label>
            <input
              v-model="managerForm.name"
              type="text"
              placeholder="Nome do colaborador"
              class="w-full text-xs border border-gray-300 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block font-bold text-gray-700 mb-1">E-mail Corporativo</label>
            <input
              v-model="managerForm.email"
              type="email"
              placeholder="colaborador@ebserh.gov.br"
              class="w-full text-xs border border-gray-300 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- 3. Perfil de Acesso -->
        <div>
          <label class="block font-bold text-gray-700 mb-1">
            Perfil de Acesso no Sistema <span class="text-rose-500">*</span>
          </label>
          <select
            v-model="managerForm.role"
            class="w-full text-xs border border-gray-300 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
          >
            <option value="GESTOR">GESTOR - Visualiza tarefas da Unidade Principal + Subordinadas + Extras</option>
            <option value="ADMINISTRADOR">ADMINISTRADOR - Gestão total e acesso irrestrito a todas as tarefas</option>
            <option value="SUPERINTENDENTE">SUPERINTENDENTE - Acesso executivo irrestrito a todas as tarefas</option>
            <option value="AUDITOR">AUDITOR - Acesso de controle/auditoria irrestrito a todas as tarefas</option>
          </select>
        </div>

        <!-- 4. Unidade Principal (Organograma HC-UFPE) -->
        <div>
          <label class="block font-bold text-gray-700 mb-1">
            Unidade Organizacional Principal (Organograma)
          </label>
          <div class="relative">
            <select
              v-model="managerForm.responsible_area_id"
              @change="onPrimaryAreaChanged"
              class="w-full text-xs border border-gray-300 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="null">Nenhuma (Acesso Global - Padrão para Administradores / Superintendência)</option>
              <optgroup
                v-for="group in groupedAreas"
                :key="group.sigla"
                :label="group.nome + ' (' + group.sigla + ')'"
              >
                <option
                  v-for="area in group.areas"
                  :key="area.id"
                  :value="area.id"
                >
                  [{{ area.level }}] {{ area.nome }} {{ area.sigla ? '(' + area.sigla + ')' : '' }}
                </option>
              </optgroup>
            </select>
          </div>
        </div>

        <!-- Previsão Dinâmica da Hierarquia de Subordinação -->
        <div
          v-if="subordinatesPreview.length > 0"
          class="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3 space-y-1.5"
        >
          <div class="flex items-center gap-1.5 font-bold text-emerald-900 text-xs">
            <CheckCircleIcon class="w-4 h-4 text-emerald-600" />
            <span>Herança Automática: {{ subordinatesPreview.length }} unidades subordinadas incluídas</span>
          </div>
          <p class="text-[11px] text-emerald-800 leading-relaxed">
            Pelo organograma (Gerência &rarr; Divisão &rarr; Setor &rarr; Unidade), este gestor visualizará automaticamente todas as tarefas destas áreas:
          </p>
          <div class="flex flex-wrap gap-1 pt-1 max-h-24 overflow-y-auto">
            <span
              v-for="sub in subordinatesPreview"
              :key="sub.id"
              class="px-2 py-0.5 bg-white text-emerald-800 border border-emerald-200 rounded text-[10px] font-medium"
            >
              {{ sub.nome }}
            </span>
          </div>
        </div>

        <!-- 5. Matriz de Unidades Extras (Checkbox Multi-Select) -->
        <div class="space-y-1.5 pt-1 border-t border-gray-100">
          <div class="flex items-center justify-between">
            <label class="block font-bold text-gray-700">
              Unidades Extras Autorizadas (Matriz de Visibilidade)
            </label>
            <span class="text-[10px] text-gray-400">Opcional</span>
          </div>
          <p class="text-[11px] text-gray-500">
            Selecione unidades adicionais que não são subordinadas naturais, mas das quais este gestor também poderá acompanhar tarefas:
          </p>

          <!-- Busca rápida de unidade extra -->
          <input
            v-model="extraUnitSearch"
            type="text"
            placeholder="Filtrar unidades extras..."
            class="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5 text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />

          <!-- Lista de Unidades com Scroll e Checkbox -->
          <div class="max-h-36 overflow-y-auto border border-gray-200 rounded-xl p-2 bg-gray-50/50 space-y-1">
            <label
              v-for="area in filteredExtraUnits"
              :key="area.id"
              class="flex items-center gap-2 px-2 py-1 rounded hover:bg-white cursor-pointer select-none text-xs transition"
              :class="{ 'bg-blue-50 font-bold text-blue-900': managerForm.extra_unit_ids.includes(area.id) }"
            >
              <input
                type="checkbox"
                :value="area.id"
                v-model="managerForm.extra_unit_ids"
                class="w-3.5 h-3.5 rounded text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span class="text-[10px] uppercase font-bold text-gray-400">[{{ area.level }}]</span>
              <span class="truncate flex-1">{{ area.nome }}</span>
              <span v-if="area.sigla" class="text-[10px] font-mono text-gray-400">{{ area.sigla }}</span>
            </label>
          </div>
        </div>

        <!-- 6. Status Ativo -->
        <div class="flex items-center gap-2 pt-2">
          <input
            type="checkbox"
            id="mgr_active"
            v-model="managerForm.is_active"
            class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-gray-300 cursor-pointer"
          />
          <label for="mgr_active" class="font-bold text-gray-700 cursor-pointer select-none">
            Gestor Ativo (Permitir Login via AD)
          </label>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end space-x-2">
          <Button variant="secondary" @click="closeManagerModal">
            Cancelar
          </Button>
          <Button variant="primary" @click="saveManager" :loading="isSavingManager">
            Salvar Gestor
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import Card from '../components/Card.vue';
import Modal from '../components/Modal.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import { auditApi, SystemManagerItem, ResponsibleArea } from '../services/auditApi';
import api from '../services/api';
import {
  Cog6ToothIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  UserPlusIcon,
  UserIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

// Lista e estado de gestores
const managersList = ref<SystemManagerItem[]>([]);
const allAreas = ref<ResponsibleArea[]>([]);
const isLoadingManagers = ref(false);
const isSavingManager = ref(false);
const managerSearchQuery = ref('');

// Modal e Formulário
const showManagerModal = ref(false);
const editingManagerId = ref<number | null>(null);
const extraUnitSearch = ref('');
const subordinatesPreview = ref<ResponsibleArea[]>([]);

const managerForm = ref({
  username: '',
  name: '',
  email: '',
  role: 'GESTOR' as 'GESTOR' | 'ADMINISTRADOR' | 'SUPERINTENDENTE' | 'AUDITOR',
  responsible_area_id: null as number | null,
  extra_unit_ids: [] as number[],
  is_active: true,
});

// Consulta AD
const isSearchingAD = ref(false);
const adSearchFeedback = ref('');
const adSearchSuccess = ref(false);

const filteredManagers = computed(() => {
  if (!managerSearchQuery.value.trim()) return managersList.value;
  const q = managerSearchQuery.value.toLowerCase().trim();
  return managersList.value.filter(
    m =>
      m.name.toLowerCase().includes(q) ||
      m.username.toLowerCase().includes(q) ||
      m.role.toLowerCase().includes(q) ||
      (m.responsible_area_nome && m.responsible_area_nome.toLowerCase().includes(q))
  );
});

const groupedAreas = computed(() => {
  const groups: Record<string, { sigla: string; nome: string; areas: ResponsibleArea[] }> = {
    SUP: { sigla: 'SUP', nome: 'Superintendência', areas: [] },
    GAD: { sigla: 'GAD', nome: 'Gerência Administrativa', areas: [] },
    GAS: { sigla: 'GAS', nome: 'Gerência de Atenção à Saúde', areas: [] },
    GEP: { sigla: 'GEP', nome: 'Gerência de Ensino e Pesquisa', areas: [] },
  };

  for (const a of allAreas.value) {
    const s = a.governance_sigla || 'SUP';
    if (groups[s]) {
      groups[s].areas.push(a);
    }
  }
  return Object.values(groups);
});

const filteredExtraUnits = computed(() => {
  let list = allAreas.value;
  // Excluir a área principal se já selecionada
  if (managerForm.value.responsible_area_id) {
    list = list.filter(a => a.id !== managerForm.value.responsible_area_id);
  }
  if (!extraUnitSearch.value.trim()) return list;
  const q = extraUnitSearch.value.toLowerCase().trim();
  return list.filter(a => a.nome.toLowerCase().includes(q) || (a.sigla && a.sigla.toLowerCase().includes(q)));
});

function getRoleBadgeClass(role: string): string {
  switch (role) {
    case 'ADMINISTRADOR':
      return 'bg-purple-100 text-purple-800 border border-purple-200';
    case 'SUPERINTENDENTE':
      return 'bg-blue-100 text-blue-800 border border-blue-200';
    case 'AUDITOR':
      return 'bg-indigo-100 text-indigo-800 border border-indigo-200';
    default:
      return 'bg-emerald-100 text-emerald-800 border border-emerald-200';
  }
}

async function loadManagers() {
  isLoadingManagers.value = true;
  try {
    managersList.value = await auditApi.listManagers();
  } catch (err) {
    console.error('Erro ao listar gestores:', err);
  } finally {
    isLoadingManagers.value = false;
  }
}

async function loadAreas() {
  try {
    allAreas.value = await auditApi.getResponsibleAreas();
  } catch (err) {
    console.error('Erro ao carregar áreas responsáveis:', err);
  }
}

async function onPrimaryAreaChanged() {
  const aid = managerForm.value.responsible_area_id;
  if (!aid) {
    subordinatesPreview.value = [];
    return;
  }
  try {
    const res = await auditApi.getSubordinates(aid);
    const subIds = new Set(res.subordinate_ids);
    subordinatesPreview.value = allAreas.value.filter(a => subIds.has(a.id));
  } catch (err) {
    console.error('Erro ao obter subordinadas:', err);
  }
}

function openAddManagerModal() {
  editingManagerId.value = null;
  managerForm.value = {
    username: '',
    name: '',
    email: '',
    role: 'GESTOR',
    responsible_area_id: null,
    extra_unit_ids: [],
    is_active: true,
  };
  subordinatesPreview.value = [];
  adSearchFeedback.value = '';
  showManagerModal.value = true;
}

async function openEditManagerModal(mgr: SystemManagerItem) {
  editingManagerId.value = mgr.id;
  managerForm.value = {
    username: mgr.username,
    name: mgr.name,
    email: mgr.email || '',
    role: mgr.role,
    responsible_area_id: mgr.responsible_area_id,
    extra_unit_ids: mgr.extra_units ? mgr.extra_units.map(u => u.id) : [],
    is_active: mgr.is_active,
  };
  adSearchFeedback.value = '';
  showManagerModal.value = true;
  if (mgr.responsible_area_id) {
    await onPrimaryAreaChanged();
  } else {
    subordinatesPreview.value = [];
  }
}

function closeManagerModal() {
  showManagerModal.value = false;
  editingManagerId.value = null;
}

async function searchAD() {
  const u = managerForm.value.username.trim();
  if (!u) return;
  isSearchingAD.value = true;
  adSearchFeedback.value = '';
  try {
    const res = await api.get(`/api/users/search/${u}`);
    if (res.data && res.data.exists) {
      adSearchSuccess.value = true;
      adSearchFeedback.value = `✓ Usuário localizado no AD: ${res.data.displayName}`;
      if (!managerForm.value.name) managerForm.value.name = res.data.displayName;
      if (!managerForm.value.email) managerForm.value.email = res.data.email;
    } else {
      adSearchSuccess.value = false;
      adSearchFeedback.value = `Usuário '${u}' não encontrado no Active Directory corporativo.`;
    }
  } catch (err) {
    adSearchSuccess.value = false;
    adSearchFeedback.value = 'Falha ao consultar servidor LDAP/AD.';
  } finally {
    isSearchingAD.value = false;
  }
}

async function saveManager() {
  if (!managerForm.value.username.trim() || !managerForm.value.name.trim()) {
    alert('Preencha os campos obrigatórios (Login AD e Nome Completo).');
    return;
  }

  isSavingManager.value = true;
  try {
    if (editingManagerId.value) {
      await auditApi.updateManager(editingManagerId.value, {
        name: managerForm.value.name,
        email: managerForm.value.email,
        role: managerForm.value.role,
        responsible_area_id: managerForm.value.responsible_area_id,
        extra_unit_ids: managerForm.value.extra_unit_ids,
        is_active: managerForm.value.is_active,
      });
    } else {
      await auditApi.createManager({
        username: managerForm.value.username,
        name: managerForm.value.name,
        email: managerForm.value.email,
        role: managerForm.value.role,
        responsible_area_id: managerForm.value.responsible_area_id,
        extra_unit_ids: managerForm.value.extra_unit_ids,
        is_active: managerForm.value.is_active,
      });
    }
    closeManagerModal();
    await loadManagers();
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Erro ao salvar gestor.';
    alert(msg);
  } finally {
    isSavingManager.value = false;
  }
}

async function confirmDeleteManager(mgr: SystemManagerItem) {
  if (confirm(`Tem certeza que deseja revogar o acesso e remover o gestor '${mgr.name}' (${mgr.username})?`)) {
    try {
      await auditApi.deleteManager(mgr.id);
      await loadManagers();
    } catch (err) {
      alert('Erro ao excluir gestor.');
    }
  }
}

onMounted(async () => {
  if (authStore.isAdmin) {
    await Promise.all([loadManagers(), loadAreas()]);
  }
});
</script>
