<template>
  <transition
    enter-active-class="transition duration-150 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-100 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="isOpen && task"
      class="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6"
      @click.self="emitClose"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl border border-gray-200 w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-150"
      >
        <!-- Cabeçalho do Modal -->
        <div class="px-6 py-5 border-b border-gray-100 bg-linear-to-r from-gray-50 via-white to-blue-50/40 flex items-start justify-between gap-4">
          <div class="space-y-1.5">
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-mono font-black text-sm bg-blue-100 text-blue-900 px-2.5 py-1 rounded-md border border-blue-200 shadow-2xs">
                Tarefa nº {{ task.task_id }}
              </span>
              
              <span v-if="task.start_year" class="text-xs font-bold bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                Ano {{ task.start_year }}
              </span>

              <!-- Badge Situação -->
              <span
                :class="getSituationBadgeClass(task.situation)"
                class="px-2.5 py-0.5 text-xs font-bold rounded-full flex items-center gap-1.5"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="getSituationDotClass(task.situation)"></span>
                {{ getSituationLabel(task.situation) }}
              </span>

              <!-- Badge Prazo -->
              <span
                :class="getPrazoBadgeClass(task.prazo_status)"
                class="px-2.5 py-0.5 text-xs font-bold rounded-full"
              >
                {{ task.prazo_status }}
                <span v-if="task.dias_restantes !== null" class="font-normal opacity-85">
                  ({{ task.dias_restantes > 0 ? '+' : '' }}{{ task.dias_restantes }}d)
                </span>
              </span>
            </div>

            <h2 class="text-lg font-bold text-gray-900 leading-snug">
              {{ task.title }}
            </h2>
          </div>

          <!-- Botão Fechar -->
          <button
            type="button"
            @click="emitClose"
            class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-xl transition cursor-pointer"
            title="Fechar (Esc)"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Conteúdo do Modal (Scrollável) -->
        <div class="p-6 overflow-y-auto space-y-6 text-xs text-gray-700">
          <!-- 1. Cartão Resumo de Governança & Metadados -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50/80 p-4 rounded-xl border border-gray-100">
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Gerência (Governança)</p>
              <p class="font-bold text-gray-900 mt-0.5 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span>
                {{ task.governance_sigla || 'Não informada' }}
                <span v-if="task.governance_nome" class="text-gray-500 font-normal truncate">
                  - {{ task.governance_nome }}
                </span>
              </p>
            </div>

            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Área Responsável</p>
              <p class="font-bold text-gray-900 mt-0.5">
                {{ task.responsible_area_nome || 'Pendente de Atribuição' }}
                <span v-if="task.responsible_area_sigla" class="text-xs font-semibold text-blue-600">
                  ({{ task.responsible_area_sigla }})
                </span>
              </p>
            </div>

            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Data Início</p>
              <p class="font-bold text-gray-900 mt-0.5">
                {{ formatDate(task.start_date) || '-' }}
              </p>
            </div>

            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Data Limite (Prazo)</p>
              <p class="font-bold text-gray-900 mt-0.5">
                {{ formatDate(task.deadline) || '-' }}
              </p>
            </div>
          </div>

          <!-- 2. Descrição Completa da Tarefa / Recomendação -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-sm text-gray-900 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                Descrição Completa da Recomendação
              </h3>
              <button
                type="button"
                @click="copyText(task.title, 'Descrição')"
                class="text-blue-600 hover:text-blue-800 text-[11px] font-semibold flex items-center gap-1 cursor-pointer"
              >
                Copiar
              </button>
            </div>
            <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 text-gray-800 leading-relaxed text-xs select-text whitespace-pre-wrap font-sans">
              {{ task.title }}
            </div>
          </div>

          <!-- 3. Texto do Monitoramento CGU -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-sm text-gray-900 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
                Texto de Monitoramento (CGU)
              </h3>
              <button
                v-if="task.monitoring_text"
                type="button"
                @click="copyText(task.monitoring_text, 'Monitoramento')"
                class="text-blue-600 hover:text-blue-800 text-[11px] font-semibold flex items-center gap-1 cursor-pointer"
              >
                Copiar
              </button>
            </div>
            <div
              v-if="task.monitoring_text"
              class="bg-blue-50/40 p-4 rounded-xl border border-blue-100 text-gray-800 leading-relaxed text-xs select-text whitespace-pre-wrap"
            >
              {{ task.monitoring_text }}
            </div>
            <p v-else class="text-xs text-gray-400 italic bg-gray-50 p-3 rounded-lg border border-dashed border-gray-200">
              Nenhum texto de monitoramento registrado para esta tarefa no e-CGU.
            </p>
          </div>

          <!-- 4. Providência Adotada / Plano de Ação -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-sm text-gray-900 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Providência Adotada / Ação
              </h3>
              <button
                v-if="task.action_taken"
                type="button"
                @click="copyText(task.action_taken, 'Providência')"
                class="text-blue-600 hover:text-blue-800 text-[11px] font-semibold flex items-center gap-1 cursor-pointer"
              >
                Copiar
              </button>
            </div>
            <div
              v-if="task.action_taken"
              class="bg-emerald-50/30 p-4 rounded-xl border border-emerald-100 text-gray-800 leading-relaxed text-xs select-text whitespace-pre-wrap"
            >
              {{ task.action_taken }}
            </div>
            <p v-else class="text-xs text-gray-400 italic bg-gray-50 p-3 rounded-lg border border-dashed border-gray-200">
              Nenhuma providência adotada informada até o momento.
            </p>
          </div>
        </div>

        <!-- Rodapé do Modal -->
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
          <span v-if="copiedMessage" class="text-xs font-semibold text-emerald-600">
            ✓ {{ copiedMessage }}
          </span>
          <span v-else class="text-[11px] text-gray-400">
            Pressione Esc ou clique fora para fechar
          </span>

          <button
            type="button"
            @click="emitClose"
            class="px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white font-semibold text-xs rounded-xl shadow-xs transition cursor-pointer"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import type { AuditTaskItem } from '../services/auditApi';

const props = defineProps<{
  isOpen: boolean;
  task: AuditTaskItem | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const copiedMessage = ref<string | null>(null);

function emitClose() {
  emit('close');
}

function formatDate(isoStr?: string | null): string {
  if (!isoStr) return '-';
  const parts = isoStr.split('T')[0].split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return isoStr;
}

function getSituationLabel(situation?: string | null): string {
  if (!situation) return 'Não informada';
  if (situation === 'Atendida') return 'Concluída';
  return situation;
}

function getSituationBadgeClass(situation?: string | null): string {
  if (situation === 'Não atendida' || situation === 'Nao atendida') {
    return 'bg-rose-50 text-rose-700 border border-rose-200';
  }
  if (situation === 'Parcialmente Atendida') {
    return 'bg-amber-50 text-amber-700 border border-amber-200';
  }
  return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
}

function getSituationDotClass(situation?: string | null): string {
  if (situation === 'Não atendida' || situation === 'Nao atendida') return 'bg-rose-500';
  if (situation === 'Parcialmente Atendida') return 'bg-amber-500';
  return 'bg-emerald-600';
}

function getPrazoBadgeClass(status?: string | null): string {
  if (status === 'Prazo Venceu') return 'bg-rose-100 text-rose-800 border border-rose-200';
  if (status === 'Prazo Encerrando') return 'bg-amber-100 text-amber-800 border border-amber-200';
  if (status === 'Prazo Amplo') return 'bg-emerald-100 text-emerald-800 border border-emerald-200';
  return 'bg-gray-100 text-gray-700';
}

function copyText(text: string, label: string) {
  navigator.clipboard.writeText(text);
  copiedMessage.value = `${label} copiada com sucesso!`;
  setTimeout(() => {
    copiedMessage.value = null;
  }, 2500);
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.isOpen) {
    emitClose();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>
