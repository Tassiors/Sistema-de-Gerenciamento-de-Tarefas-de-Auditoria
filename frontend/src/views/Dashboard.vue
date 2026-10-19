<template>
  <div class="space-y-6">
    <!-- Header Principal -->
    <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center space-x-4">
        <div class="p-3 bg-blue-50 text-blue-700 rounded-2xl border border-blue-100 flex items-center justify-center shadow-inner">
          <ChartBarIcon class="w-8 h-8" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-black tracking-widest uppercase px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
              HC-UFPE / EBSERH
            </span>
            <span class="text-xs font-semibold text-gray-500">Monitoramento e-CGU</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-black text-gray-900 tracking-tight mt-1">
            {{ activeFilter === 'GERAL' ? 'QUADRO GERAL' : getGerenciaNome(activeFilter) }}
          </h1>
          <p class="text-xs text-gray-500 mt-0.5">
            Acompanhamento de apontamentos de auditoria, prazos de vencimento e providências adotadas.
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <router-link
          to="/importar"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-sm transition"
        >
          <ArrowUpTrayIcon class="w-4 h-4" />
          Importar Planilha e-CGU
        </router-link>
      </div>
    </div>

    <!-- Navegador de Gerências (Estilo Bookmarks Power BI) -->
    <div class="bg-white border border-gray-200 rounded-2xl p-2 shadow-sm flex flex-wrap items-center gap-2">
      <button
        v-for="b in bookmarkOptions"
        :key="b.key"
        @click="selectFilter(b.key)"
        :class="[
          'px-5 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2 relative overflow-hidden',
          activeFilter === b.key
            ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20 ring-2 ring-blue-600/30'
            : 'bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-900 border border-gray-100'
        ]"
      >
        <span
          v-if="activeFilter === b.key"
          class="w-1.5 h-3.5 bg-amber-400 rounded-full"
        ></span>
        {{ b.label }}
      </button>
    </div>

    <!-- Cards KPI -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <!-- Total Tarefas Pendentes -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex items-center justify-between border-l-4 border-l-blue-600">
        <div>
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Tarefas Pendentes</p>
          <p class="text-3xl md:text-4xl font-black text-blue-900 mt-1">
            {{ metrics?.kpis.total_pendentes ?? 0 }}
          </p>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">
              {{ activeFilter === 'GERAL' ? 'Todas as Gerências' : getGerenciaNome(activeFilter) }}
            </span>
            <span
              v-if="(metrics?.kpis.pendentes_sem_area ?? 0) > 0"
              class="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md flex items-center gap-1"
            >
              ⚠ {{ metrics?.kpis.pendentes_sem_area }} sem setor
            </span>
          </div>
        </div>
        <div class="p-3 bg-blue-50 text-blue-600 rounded-2xl">
          <ClockIcon class="w-8 h-8" />
        </div>
      </div>

      <!-- Total Tarefas Atendidas -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex items-center justify-between border-l-4 border-l-emerald-600">
        <div>
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Tarefas Atendidas</p>
          <p class="text-3xl md:text-4xl font-black text-emerald-900 mt-1">
            {{ metrics?.kpis.total_atendidas ?? 0 }}
          </p>
          <p class="text-xs font-semibold text-emerald-600 mt-2">
            (A partir de Maio/24)
          </p>
        </div>
        <div class="p-3 bg-emerald-50 text-emerald-600 rounded-2xl">
          <CheckBadgeIcon class="w-8 h-8" />
        </div>
      </div>

      <!-- Total Ativas / Resumo -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex items-center justify-between border-l-4 border-l-gray-400">
        <div>
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wider">Total em Acompanhamento</p>
          <p class="text-3xl md:text-4xl font-black text-gray-800 mt-1">
            {{ metrics?.kpis.total_ativas ?? 0 }}
          </p>
          <p class="text-xs text-gray-500 mt-2">
            Taxa de atendimento: <strong class="text-gray-900">{{ calcTaxaAtendimento }}%</strong>
          </p>
        </div>
        <div class="p-3 bg-gray-50 text-gray-600 rounded-2xl">
          <DocumentCheckIcon class="w-8 h-8" />
        </div>
      </div>
    </div>

    <!-- Seção de Gráficos Analíticos -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- 1. Tarefas Pendentes x Situação -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-gray-100">
            <h3 class="font-bold text-sm text-gray-900">Tarefas Pendentes x Situação</h3>
            <span class="text-[11px] text-gray-400 font-medium">Providências</span>
          </div>

          <div class="space-y-4 pt-4">
            <div v-for="item in metrics?.situacao" :key="item.situacao">
              <div class="flex items-center justify-between text-xs mb-1">
                <span class="font-bold text-gray-700 flex items-center gap-1.5">
                  <span
                    :class="[
                      'w-2.5 h-2.5 rounded-full',
                      item.situacao === 'Não atendida' ? 'bg-rose-500' : 'bg-amber-400'
                    ]"
                  ></span>
                  {{ item.situacao }}
                </span>
                <span class="font-black text-gray-900">
                  {{ item.quantidade }}
                  <span class="text-gray-400 font-normal">({{ calcPercent(item.quantidade, metrics?.kpis.total_pendentes) }}%)</span>
                </span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div
                  :class="[
                    'h-3 rounded-full transition-all duration-500',
                    item.situacao === 'Não atendida' ? 'bg-rose-400' : 'bg-amber-300'
                  ]"
                  :style="{ width: calcPercent(item.quantidade, metrics?.kpis.total_pendentes) + '%' }"
                ></div>
              </div>
            </div>

            <div v-if="!metrics?.situacao || metrics.situacao.length === 0" class="text-center py-6 text-xs text-gray-400">
              Nenhuma pendência ativa para a gerência selecionada.
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
          <span>Total: {{ metrics?.kpis.total_pendentes }}</span>
          <span>Status oficial e-CGU</span>
        </div>
      </div>

      <!-- 2. Tarefas Pendentes x Prazo -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-gray-100">
            <h3 class="font-bold text-sm text-gray-900">Tarefas Pendentes x Prazo</h3>
            <span class="text-[11px] text-gray-400 font-medium">Semáforo</span>
          </div>

          <div class="space-y-4 pt-4">
            <div v-for="item in metrics?.prazo" :key="item.status">
              <div class="flex items-center justify-between text-xs mb-1">
                <span class="font-bold text-gray-700 flex items-center gap-1.5">
                  <span
                    :class="[
                      'w-2.5 h-2.5 rounded-full',
                      item.status === 'Prazo Amplo' ? 'bg-emerald-500' :
                      item.status === 'Prazo Encerrando' ? 'bg-amber-400' : 'bg-rose-500'
                    ]"
                  ></span>
                  {{ item.status }}
                </span>
                <span class="font-black text-gray-900">
                  {{ item.quantidade }}
                </span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div
                  :class="[
                    'h-3 rounded-full transition-all duration-500',
                    item.status === 'Prazo Amplo' ? 'bg-blue-300' :
                    item.status === 'Prazo Encerrando' ? 'bg-amber-200' : 'bg-rose-400'
                  ]"
                  :style="{ width: calcPercent(item.quantidade, metrics?.kpis.total_pendentes) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
          <span>Amplo (>20d) &bull; Encerrando (≤20d) &bull; Venceu</span>
        </div>
      </div>

      <!-- 3. Tarefas Pendentes x Ano de Origem -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-gray-100">
            <h3 class="font-bold text-sm text-gray-900">Tarefas Pendentes x Ano</h3>
            <span class="text-[11px] text-gray-400 font-medium">Origem</span>
          </div>

          <div class="pt-6 flex items-end justify-around h-36 gap-3">
            <div
              v-for="item in metrics?.por_ano"
              :key="item.ano"
              class="flex flex-col items-center flex-1 h-full justify-end group"
            >
              <span class="text-xs font-black text-gray-800 mb-1 group-hover:scale-110 transition-transform">
                {{ item.quantidade }}
              </span>
              <div
                class="w-full max-w-[38px] bg-emerald-400 group-hover:bg-emerald-500 rounded-t-lg transition-all duration-500"
                :style="{ height: calcAnoHeight(item.quantidade) }"
              ></div>
              <span class="text-[11px] font-bold text-gray-500 mt-2">{{ item.ano }}</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-gray-100 text-center text-[11px] text-gray-400">
          Ano da Data de Início da Recomendação
        </div>
      </div>
    </div>

    <!-- Série Histórica RNA (Recomendações Não Atendidas) -->
    <div v-if="activeFilter === 'GERAL'" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex items-center justify-between pb-2 border-b border-gray-100">
        <div>
          <h3 class="font-bold text-sm text-gray-900">Recomendações Não Atendidas (A partir de MAIO/24)</h3>
          <p class="text-xs text-gray-500">Histórico temporal da curva de redução de passivo de auditoria do HC-UFPE.</p>
        </div>
        <span class="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
          Tendência Mensal
        </span>
      </div>

      <!-- Gráfico SVG customizado e responsivo -->
      <div class="overflow-x-auto py-2">
        <div class="min-w-[750px] h-48 relative">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 750 160">
            <!-- Linhas de grade sutis -->
            <line x1="20" y1="30" x2="730" y2="30" stroke="#f1f5f9" stroke-width="1" />
            <line x1="20" y1="80" x2="730" y2="80" stroke="#f1f5f9" stroke-width="1" />
            <line x1="20" y1="130" x2="730" y2="130" stroke="#f1f5f9" stroke-width="1" />

            <!-- Caminho / Linha da Série Temporal -->
            <path
              :d="generateRnaPath(750, 140)"
              fill="none"
              stroke="#0284c7"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            />

            <!-- Pontos e Rótulos -->
            <g v-for="(pt, idx) in calculateRnaPoints(750, 140)" :key="idx" class="cursor-pointer group">
              <circle
                :cx="pt.x"
                :cy="pt.y"
                r="4.5"
                fill="#0284c7"
                class="group-hover:r-6 transition-all"
              />
              <text
                :x="pt.x"
                :y="pt.y - 10"
                text-anchor="middle"
                class="text-[11px] font-black fill-gray-800"
              >
                {{ pt.valor }}
              </text>
              <text
                :x="pt.x"
                y="155"
                text-anchor="middle"
                class="text-[9px] font-semibold fill-gray-400"
              >
                {{ pt.mesCurto }}
              </text>
            </g>
          </svg>
        </div>
      </div>
    </div>

    <!-- Tabela Operacional de Tarefas -->
    <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
      <!-- Toolbar da Tabela -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h3 class="font-bold text-base text-gray-900 flex items-center gap-2">
            <TableCellsIcon class="w-5 h-5 text-gray-600" />
            Tarefas de Auditoria
          </h3>
          <p class="text-xs text-gray-500">Listagem detalhada com atribuição rápida de Área Responsável.</p>
        </div>

        <!-- Legenda de Prazos -->
        <div class="flex flex-wrap items-center gap-3 text-xs bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-100">
          <span class="font-bold text-gray-500 text-[11px] uppercase">Legenda:</span>
          <span class="flex items-center gap-1 font-semibold text-emerald-700">
            🟢 Prazo Amplo (&gt;20 dias)
          </span>
          <span class="flex items-center gap-1 font-semibold text-amber-700">
            🟡 Prazo Encerrando (≤20 dias)
          </span>
          <span class="flex items-center gap-1 font-semibold text-rose-700">
            🔴 Prazo Venceu (≤0 dias)
          </span>
        </div>
      </div>

      <!-- Filtros da Tabela -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3 bg-gray-50/70 p-3 rounded-xl border border-gray-100">
        <!-- Busca Textual -->
        <div class="relative">
          <input
            v-model="filters.search"
            @input="debouncedFetchTasks"
            type="text"
            placeholder="Buscar por ID, Título ou Texto..."
            class="w-full text-xs bg-white border border-gray-300 rounded-lg pl-8 pr-3 py-2 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <MagnifyingGlassIcon class="w-4 h-4 text-gray-400 absolute left-2.5 top-2.5" />
        </div>

        <!-- Filtro Situação -->
                <!-- Filtro de Situao de Mltipla Escolha -->
        <div class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 p-1 rounded-xl">
          <span class="text-[11px] font-bold text-gray-500 px-2">Situao:</span>
          <button
            type="button"
            v-for="sit in availableSituations"
            :key="sit"
            @click="toggleSituationFilter(sit)"
            :class="[
              selectedSituations.includes(sit)
                ? (sit === 'No atendida' ? 'bg-rose-600 text-white shadow-xs font-semibold' :
                   sit === 'Parcialmente Atendida' ? 'bg-amber-500 text-white shadow-xs font-semibold' :
                   'bg-emerald-600 text-white shadow-xs font-semibold')
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            ]"
            class="px-2.5 py-1 text-xs rounded-lg transition-all flex items-center gap-1.5 select-none cursor-pointer"
          >
            <span
              class="w-2 h-2 rounded-full"
              :class="[
                sit === 'No atendida' ? (selectedSituations.includes(sit) ? 'bg-white' : 'bg-rose-500') :
                sit === 'Parcialmente Atendida' ? (selectedSituations.includes(sit) ? 'bg-white' : 'bg-amber-500') :
                (selectedSituations.includes(sit) ? 'bg-white' : 'bg-emerald-600')
              ]"
            ></span>
            {{ sit }}
          </button>
        </div>

        <!-- Filtro Prazo -->
        <select
          v-model="filters.prazo"
          @change="fetchTasks"
          class="text-xs bg-white border border-gray-300 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todos os Prazos</option>
          <option value="Prazo Amplo">Prazo Amplo (&gt;20d)</option>
          <option value="Prazo Encerrando">Prazo Encerrando (≤20d)</option>
          <option value="Prazo Venceu">Prazo Venceu (≤0d)</option>
        </select>

        <!-- Filtro Especial: Sem Área -->
        <div class="flex items-center justify-between gap-2">
          <label class="flex items-center gap-2 cursor-pointer text-xs font-semibold text-gray-700">
            <input
              type="checkbox"
              v-model="filters.unassigned"
              @change="fetchTasks"
              class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            Apenas sem setor
          </label>
          <button
            @click="resetFilters"
            class="text-xs text-gray-500 hover:text-gray-900 font-semibold px-2 py-1 rounded bg-white border border-gray-200"
          >
            Limpar
          </button>
        </div>
      </div>

      <!-- Tabela -->
      <div class="overflow-x-auto border border-gray-200 rounded-xl">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="bg-gray-100/70 text-gray-700 font-black uppercase text-[10px] tracking-wider border-b border-gray-200">
              <th class="py-3 px-3 w-16">Ano</th>
              <th class="py-3 px-3 w-24">Tarefa</th>
              <th class="py-3 px-4">Descrição / Título da Tarefa</th>
              <th class="py-3 px-3 w-28">Data Limite</th>
              <th class="py-3 px-3 w-32">Prazo</th>
              <th class="py-3 px-3 w-32">Situação</th>
              <th class="py-3 px-3 w-48">Área Responsável</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="task in tasksList"
              :key="task.id"
              class="hover:bg-blue-50/40 transition-colors"
            >
              <td class="py-3 px-3 font-bold text-gray-600">{{ task.start_year || '-' }}</td>
              <td class="py-3 px-3 font-black text-blue-700 font-mono">{{ task.task_id }}</td>
              <td class="py-3 px-4">
                <p class="font-bold text-gray-900 leading-tight line-clamp-1" :title="task.title">{{ task.title }}</p>
                <p v-if="task.monitoring_text" class="text-[11px] text-gray-500 line-clamp-2 mt-0.5" :title="task.monitoring_text">
                  {{ task.monitoring_text }}
                </p>
              </td>
              <td class="py-3 px-3 font-semibold text-gray-700 whitespace-nowrap">
                {{ formatDate(task.deadline) }}
              </td>
              <td class="py-3 px-3 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold',
                    task.prazo_status === 'Prazo Amplo' ? 'bg-emerald-100 text-emerald-800' :
                    task.prazo_status === 'Prazo Encerrando' ? 'bg-amber-100 text-amber-800' :
                    task.prazo_status === 'Prazo Venceu' ? 'bg-rose-100 text-rose-800' : 'bg-gray-100 text-gray-700'
                  ]"
                >
                  <span v-if="task.prazo_status === 'Prazo Amplo'">🟢</span>
                  <span v-else-if="task.prazo_status === 'Prazo Encerrando'">🟡</span>
                  <span v-else-if="task.prazo_status === 'Prazo Venceu'">🔴</span>
                  {{ task.prazo_status }}
                  <span v-if="task.dias_restantes !== null" class="text-[10px] opacity-75">({{ task.dias_restantes }}d)</span>
                </span>
              </td>
              <td class="py-3 px-3 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-0.5 rounded font-bold text-[11px]',
                    task.situation === 'Concluída' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                    task.situation === 'Parcialmente Atendida' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                    'bg-rose-50 text-rose-700 border border-rose-200'
                  ]"
                >
                  {{ task.situation || 'Não atendida' }}
                </span>
              </td>
              <td class="py-3 px-3">
                <div class="flex items-center justify-between gap-1">
                  <span
                    v-if="task.responsible_area_nome"
                    class="font-semibold text-gray-800 text-[11px] line-clamp-1"
                    :title="task.responsible_area_nome"
                  >
                    {{ task.responsible_area_nome }}
                  </span>
                  <span v-else class="text-[11px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    Não atribuído
                  </span>
                  <button
                    @click="openAssignModal(task)"
                    class="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition"
                    title="Atribuir ou alterar setor responsável"
                  >
                    <PencilSquareIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="tasksList.length === 0">
              <td colspan="7" class="py-10 text-center text-gray-400 text-xs">
                Nenhuma tarefa encontrada com os filtros selecionados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginação -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs text-gray-600">
        <p>Mostrando {{ tasksList.length }} de {{ totalTasks }} tarefas</p>
        <div class="flex items-center space-x-2">
          <button
            @click="prevPage"
            :disabled="currentPage <= 1"
            class="px-3 py-1.5 border border-gray-300 rounded-lg bg-white disabled:opacity-40 hover:bg-gray-50 transition font-bold"
          >
            Anterior
          </button>
          <span class="font-bold text-gray-800">Página {{ currentPage }} de {{ totalPages }}</span>
          <button
            @click="nextPage"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1.5 border border-gray-300 rounded-lg bg-white disabled:opacity-40 hover:bg-gray-50 transition font-bold"
          >
            Próxima
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Atribuição de Área Responsável -->
    <div
      v-if="selectedTaskForAssign"
      class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-xs"
      @click.self="closeAssignModal"
    >
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-base font-bold text-gray-900">
            Atribuir Área Responsável
          </h3>
          <button @click="closeAssignModal" class="text-gray-400 hover:text-gray-600 font-black">✕</button>
        </div>

        <div class="space-y-3 text-xs">
          <div class="bg-blue-50 p-3 rounded-xl border border-blue-100">
            <p class="font-bold text-blue-900">Tarefa #{{ selectedTaskForAssign.task_id }}</p>
            <p class="text-gray-700 mt-1 line-clamp-2">{{ selectedTaskForAssign.title }}</p>
          </div>

                <div>
        <label class="block font-bold text-gray-700 mb-1">Buscar Unidade do Organograma HC-UFPE:</label>
        <input
          v-model="modalAreaSearch"
          type="text"
          placeholder="Filtrar unidade (ex: SETISD, Compras, Qualidade)..."
          class="w-full text-xs border border-gray-300 rounded-lg p-2 mb-2 bg-gray-50 text-gray-800 focus:ring-2 focus:ring-blue-500"
        />
        <label class="block font-bold text-gray-700 mb-1">Selecione a Unidade Organizacional:</label>
        <select
          v-model="modalSelectedAreaId"
          class="w-full text-xs border border-gray-300 rounded-lg p-2.5 bg-white text-gray-800 focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">-- Nenhuma (Remover Atribuio) --</option>
          <optgroup v-for="gov in filteredGovUnitsForModal" :key="gov.id" :label="gov.sigla + ' - ' + gov.nome">
            <option v-for="area in gov.areas" :key="area.id" :value="area.id">
              {{ area.nome }}
            </option>
          </optgroup>
        </select>
      </div>
        </div>

        <div class="flex justify-end gap-2 pt-3 border-t">
          <button
            @click="closeAssignModal"
            class="px-4 py-2 text-xs font-bold text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            Cancelar
          </button>
          <button
            @click="saveAreaAssignment"
            class="px-5 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm"
          >
            Salvar Atribuição
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  ChartBarIcon,
  ClockIcon,
  CheckBadgeIcon,
  DocumentCheckIcon,
  TableCellsIcon,
  MagnifyingGlassIcon,
  PencilSquareIcon,
  ArrowUpTrayIcon,
} from '@heroicons/vue/24/outline';
import { auditApi, DashboardMetrics, AuditTaskItem, GovernanceUnit } from '../services/auditApi';

const bookmarkOptions = [
  { key: 'GERAL', label: 'QUADRO GERAL' },
  { key: 'SUP', label: 'SUPERINTENDÊNCIA (SUP)' },
  { key: 'GAD', label: 'GERÊNCIA ADMINISTRATIVA (GAD)' },
  { key: 'GAS', label: 'GERÊNCIA DE ATENÇÃO À SAÚDE (GAS)' },
  { key: 'GEP', label: 'GERÊNCIA DE ENSINO E PESQUISA (GEP)' },
];

const activeFilter = ref('GERAL');
const metrics = ref<DashboardMetrics | null>(null);
const tasksList = ref<AuditTaskItem[]>([]);
const totalTasks = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const allGovUnits = ref<GovernanceUnit[]>([]);

const filters = ref({
  search: '',
  situation: '',
  prazo: '',
  unassigned: false,
});

const selectedTaskForAssign = ref<AuditTaskItem | null>(null);
const modalSelectedAreaId = ref<number | null>(null);
const availableSituations = ['No atendida', 'Parcialmente Atendida', 'Atendida'];
const selectedSituations = ref<string[]>(['No atendida', 'Parcialmente Atendida']);
const modalAreaSearch = ref('');

const filteredGovUnitsForModal = computed(() => {
  if (!modalAreaSearch.value.trim()) {
    return allGovUnits.value;
  }
  const term = modalAreaSearch.value.toLowerCase().trim();
  return allGovUnits.value
    .map(gov => ({
      ...gov,
      areas: gov.areas.filter(a => a.nome.toLowerCase().includes(term) || gov.sigla.toLowerCase().includes(term))
    }))
    .filter(gov => gov.areas.length > 0);
});

function toggleSituationFilter(sit: string) {
  if (selectedSituations.value.includes(sit)) {
    selectedSituations.value = selectedSituations.value.filter(s => s !== sit);
  } else {
    selectedSituations.value.push(sit);
  }
  currentPage.value = 1;
  fetchTasks();
}


let debounceTimeout: any = null;

function getGerenciaNome(sigla: string) {
  const map: Record<string, string> = {
    SUP: 'SUPERINTENDÊNCIA',
    GAD: 'GERÊNCIA ADMINISTRATIVA',
    GAS: 'GERÊNCIA DE ATENÇÃO À SAÚDE',
    GEP: 'GERÊNCIA DE ENSINO E PESQUISA',
  };
  return map[sigla] || sigla;
}

const calcTaxaAtendimento = computed(() => {
  if (!metrics.value || metrics.value.kpis.total_ativas === 0) return 0;
  return Math.round((metrics.value.kpis.total_atendidas / metrics.value.kpis.total_ativas) * 100);
});

function calcAnoHeight(quantidade: number) {
  if (!metrics.value || !metrics.value.por_ano || metrics.value.por_ano.length === 0) return '20px';
  const maxQ = Math.max(...metrics.value.por_ano.map(a => a.quantidade), 1);
  return Math.max((quantidade / maxQ) * 100, 15) + 'px';
}

function calcPercent(val: number, total?: number) {
  if (!total || total === 0) return 0;
  return Math.round((val / total) * 100);
}

function formatDate(dStr: string | null) {
  if (!dStr) return '-';
  const parts = dStr.split('-');
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
  return dStr;
}

async function selectFilter(key: string) {
  activeFilter.value = key;
  currentPage.value = 1;
  await Promise.all([fetchMetrics(), fetchTasks()]);
}

async function fetchMetrics() {
  try {
    const sigla = activeFilter.value === 'GERAL' ? undefined : activeFilter.value;
    metrics.value = await auditApi.getDashboard(sigla);
  } catch (err) {
    console.error('Erro ao buscar métricas:', err);
  }
}

async function fetchTasks() {
  try {
    const sigla = activeFilter.value === 'GERAL' ? undefined : activeFilter.value;
    const res = await auditApi.getTasks({
      page: currentPage.value,
      page_size: 25,
      search: filters.value.search || undefined,
      sigla: sigla,
      situation: selectedSituations.value.length > 0 ? selectedSituations.value.join(',') : undefined,
      prazo: filters.value.prazo || undefined,
      unassigned: filters.value.unassigned ? true : undefined,
    });
    tasksList.value = res.items;
    totalTasks.value = res.total;
    totalPages.value = res.total_pages;
  } catch (err) {
    console.error('Erro ao buscar tarefas:', err);
  }
}

function debouncedFetchTasks() {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    currentPage.value = 1;
    fetchTasks();
  }, 350);
}

function resetFilters() {
  selectedSituations.value = ['No atendida', 'Parcialmente Atendida'];
  filters.value = {
    search: '',
    situation: '',
    prazo: '',
    unassigned: false,
  };
  currentPage.value = 1;
  fetchTasks();
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchTasks();
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchTasks();
  }
}

function openAssignModal(task: AuditTaskItem) {
  selectedTaskForAssign.value = task;
  modalSelectedAreaId.value = task.responsible_area_id;
}

function closeAssignModal() {
  selectedTaskForAssign.value = null;
  modalSelectedAreaId.value = null;
}

async function saveAreaAssignment() {
  if (!selectedTaskForAssign.value) return;
  try {
    await auditApi.assignResponsibleArea(
      selectedTaskForAssign.value.task_id,
      modalSelectedAreaId.value,
    );
    closeAssignModal();
    await Promise.all([fetchMetrics(), fetchTasks()]);
  } catch (err) {
    alert('Erro ao atualizar área responsável.');
  }
}

// Helpers para o Gráfico SVG da Série Histórica RNA
function calculateRnaPoints(width: number, height: number) {
  const data = metrics.value?.rna_historico || [];
  if (data.length === 0) return [];
  const maxVal = Math.max(...data.map(d => d.quantidade), 140);
  const minVal = 0;
  const paddingX = 40;
  const usableWidth = width - paddingX * 2;
  const stepX = usableWidth / (data.length - 1);

  return data.map((d, i) => {
    const x = paddingX + i * stepX;
    const normY = (d.quantidade - minVal) / (maxVal - minVal);
    const y = height - normY * (height - 40) - 10;
    const mesCurto = d.label.includes(' de ')
      ? d.label.split(' de ')[0].substring(0, 3) + '/' + d.label.split(' de ')[1]?.substring(2)
      : d.label;
    return { x, y, valor: d.quantidade, mesCurto };
  });
}

function generateRnaPath(width: number, height: number) {
  const points = calculateRnaPoints(width, height);
  if (points.length === 0) return '';
  return points.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`, '');
}

onMounted(async () => {
  try {
    allGovUnits.value = await auditApi.getGovernanceUnits();
  } catch (e) {
    console.error(e);
  }
  await Promise.all([fetchMetrics(), fetchTasks()]);
});
</script>
