<template>
  <div class="space-y-6 max-w-5xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-gray-200">
      <div>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
          <ArrowUpTrayIcon class="w-7 h-7 text-blue-600" />
          Importação de Planilha do e-CGU
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Faça o upload do relatório oficial exportado do sistema e-CGU (.xlsx) para atualizar automaticamente o estoque de tarefas e providências.
        </p>
      </div>
      <router-link
        to="/"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition shadow-sm"
      >
        <ArrowLeftIcon class="w-4 h-4" />
        Voltar ao Dashboard
      </router-link>
    </div>

    <!-- Área de Drag & Drop -->
    <div
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="[
        'border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer bg-white shadow-sm',
        isDragging ? 'border-blue-500 bg-blue-50/50 scale-[1.01]' : 'border-gray-300 hover:border-blue-400'
      ]"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".xlsx,.xls"
        class="hidden"
        @change="handleFileSelect"
      />

      <div class="flex flex-col items-center justify-center space-y-3">
        <div class="p-4 bg-blue-100/70 text-blue-600 rounded-full">
          <DocumentArrowUpIcon class="w-10 h-10" />
        </div>
        <div class="space-y-1">
          <p class="text-base font-bold text-gray-800">
            Arraste e solte o arquivo <span class="text-blue-600">.xlsx</span> do e-CGU aqui
          </p>
          <p class="text-xs text-gray-500">ou clique para selecionar no seu computador</p>
        </div>
        <p class="text-[11px] text-gray-400">Suporta arquivos Excel gerados em https://ecgu.cgu.gov.br/</p>
      </div>
    </div>

    <!-- Arquivo Selecionado -->
    <div v-if="selectedFile" class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-emerald-100 text-emerald-700 rounded-lg">
          <DocumentTextIcon class="w-6 h-6" />
        </div>
        <div>
          <p class="text-sm font-bold text-gray-800">{{ selectedFile.name }}</p>
          <p class="text-xs text-gray-500">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <button
          @click.stop="clearFile"
          :disabled="isUploading"
          class="text-xs text-gray-500 hover:text-red-600 px-3 py-1.5 rounded transition disabled:opacity-50"
        >
          Remover
        </button>
        <button
          @click.stop="processUpload"
          :disabled="isUploading"
          class="inline-flex items-center gap-2 px-5 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition disabled:opacity-50"
        >
          <span v-if="isUploading" class="inline-block animate-spin mr-1">⏳</span>
          {{ isUploading ? 'Processando dados...' : 'Processar e Atualizar Base' }}
        </button>
      </div>
    </div>

    <!-- Erro -->
    <div v-if="errorMessage" class="p-4 bg-red-50 border-l-4 border-red-500 text-red-800 rounded-lg text-sm flex items-start gap-3">
      <ExclamationTriangleIcon class="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
      <div>
        <p class="font-bold">Falha no processamento</p>
        <p class="text-xs mt-0.5">{{ errorMessage }}</p>
      </div>
    </div>

    <!-- Resumo da Carga -->
    <div v-if="importResult" class="bg-white border border-emerald-200 rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-emerald-100 text-emerald-600 rounded-full">
          <CheckCircleIcon class="w-7 h-7" />
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Importação Concluída com Sucesso!</h2>
          <p class="text-xs text-gray-500">Lote #{{ importResult.batch_id }} &bull; Arquivo: {{ importResult.filename }}</p>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
        <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total de Linhas</p>
          <p class="text-2xl font-black text-gray-900 mt-1">{{ importResult.total_rows }}</p>
          <p class="text-[11px] text-gray-400 mt-0.5">no arquivo e-CGU</p>
        </div>

        <div class="p-4 bg-blue-50 rounded-xl border border-blue-100">
          <p class="text-xs font-semibold text-blue-700 uppercase tracking-wider">Tarefas Ativas</p>
          <p class="text-2xl font-black text-blue-800 mt-1">{{ importResult.active_rows }}</p>
          <p class="text-[11px] text-blue-600 mt-0.5">vigentes no painel</p>
        </div>

        <div class="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
          <p class="text-xs font-semibold text-emerald-700 uppercase tracking-wider">Novas Inseridas</p>
          <p class="text-2xl font-black text-emerald-800 mt-1">{{ importResult.inserted_count }}</p>
          <p class="text-[11px] text-emerald-600 mt-0.5">cadastradas no banco</p>
        </div>

        <div class="p-4 bg-amber-50 rounded-xl border border-amber-100">
          <p class="text-xs font-semibold text-amber-700 uppercase tracking-wider">Atualizadas</p>
          <p class="text-2xl font-black text-amber-800 mt-1">{{ importResult.updated_count }}</p>
          <p class="text-[11px] text-amber-600 mt-0.5">preservando áreas</p>
        </div>
      </div>

      <div class="flex justify-end pt-2">
        <router-link
          to="/"
          class="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg shadow-sm transition"
        >
          Visualizar Indicadores no Dashboard
          <ArrowRightIcon class="w-4 h-4" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  ArrowUpTrayIcon,
  DocumentArrowUpIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
} from '@heroicons/vue/24/outline';
import { auditApi } from '../services/auditApi';

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const isDragging = ref(false);
const isUploading = ref(false);
const errorMessage = ref<string | null>(null);
const importResult = ref<any | null>(null);

function triggerFileInput() {
  fileInput.value?.click();
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
    errorMessage.value = null;
    importResult.value = null;
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false;
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0];
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      selectedFile.value = file;
      errorMessage.value = null;
      importResult.value = null;
    } else {
      errorMessage.value = 'Por favor, selecione apenas arquivos do Excel (.xlsx ou .xls).';
    }
  }
}

function clearFile() {
  selectedFile.value = null;
  errorMessage.value = null;
  importResult.value = null;
  if (fileInput.value) fileInput.value.value = '';
}

async function processUpload() {
  if (!selectedFile.value) return;

  isUploading.value = true;
  errorMessage.value = null;
  importResult.value = null;

  try {
    const res = await auditApi.uploadEcguFile(selectedFile.value);
    importResult.value = res.data;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || err.message || 'Erro ao processar o arquivo.';
  } finally {
    isUploading.value = false;
  }
}
</script>
