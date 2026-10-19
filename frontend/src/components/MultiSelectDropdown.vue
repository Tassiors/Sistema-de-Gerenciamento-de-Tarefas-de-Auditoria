<template>
  <div class="relative inline-block w-full text-left" ref="dropdownRef">
    <!-- Botão Dropdown / Dropbox -->
    <button
      type="button"
      @click="isOpen = !isOpen"
      :class="[
        isOpen ? 'ring-2 ring-blue-500 border-blue-400 bg-white' : 'border-gray-300 bg-white hover:bg-gray-50',
        'w-full flex items-center justify-between gap-2 px-3 py-2 text-xs font-medium text-gray-700 bg-white border rounded-lg shadow-2xs transition-all cursor-pointer'
      ]"
      :aria-expanded="isOpen"
    >
      <div class="flex items-center gap-1.5 min-w-0 truncate">
        <span class="font-bold text-gray-500 uppercase text-[10px] tracking-wide">{{ label }}:</span>
        
        <!-- Rótulo / Resumo dos Itens Selecionados -->
        <span v-if="selectedCount === 0" class="text-gray-400 font-normal truncate">
          {{ placeholder || 'Todos' }}
        </span>
        <span v-else-if="selectedCount === options.length" class="text-blue-700 font-semibold truncate">
          Todos ({{ selectedCount }})
        </span>
        <div v-else class="flex items-center gap-1 min-w-0 truncate">
          <span class="font-semibold text-gray-900 truncate">
            {{ displaySummary }}
          </span>
          <span
            v-if="selectedCount > 1"
            class="ml-1 px-1.5 py-0.5 text-[10px] font-bold bg-blue-100 text-blue-700 rounded-full"
          >
            +{{ selectedCount - 1 }}
          </span>
        </div>
      </div>

      <!-- Ícone Chevron -->
      <svg
        class="w-4 h-4 text-gray-400 transition-transform duration-200 shrink-0"
        :class="{ 'rotate-180 text-blue-600': isOpen }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Painel Suspenso de Seleção (Dropdown) -->
    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0 -translate-y-1"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute left-0 z-50 w-64 mt-1.5 origin-top-left bg-white border border-gray-200 rounded-xl shadow-xl ring-1 ring-black/5 divide-y divide-gray-100 focus:outline-none"
      >
        <!-- Ações Rápidas (Marcar / Desmarcar Todos) -->
        <div class="px-3 py-2 bg-gray-50/80 rounded-t-xl flex items-center justify-between text-[11px] font-semibold">
          <span class="text-gray-500">Lógica: <strong class="text-blue-600">OU (OR)</strong></span>
          <div class="flex items-center gap-2">
            <button
              type="button"
              @click="selectAll"
              class="text-blue-600 hover:text-blue-800 transition-colors cursor-pointer"
            >
              Todos
            </button>
            <span class="text-gray-300">|</span>
            <button
              type="button"
              @click="clearAll"
              class="text-gray-500 hover:text-gray-700 transition-colors cursor-pointer"
            >
              Limpar
            </button>
          </div>
        </div>

        <!-- Lista de Opções com Checkboxes -->
        <div class="p-1.5 max-h-56 overflow-y-auto space-y-0.5">
          <label
            v-for="opt in options"
            :key="opt.value"
            class="flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs cursor-pointer select-none transition-colors hover:bg-gray-100/80"
            :class="{ 'bg-blue-50/60 font-semibold text-blue-900': isSelected(opt.value) }"
          >
            <input
              type="checkbox"
              :checked="isSelected(opt.value)"
              @change="toggleOption(opt.value)"
              class="w-3.5 h-3.5 rounded text-blue-600 focus:ring-blue-500 border-gray-300 transition"
            />

            <!-- Ponto colorido indicador se aplicável -->
            <span
              v-if="opt.colorClass"
              class="w-2.5 h-2.5 rounded-full shrink-0"
              :class="opt.colorClass"
            ></span>

            <!-- Texto da Opção -->
            <span class="truncate flex-1 text-gray-700 font-medium">
              {{ opt.label }}
            </span>

            <!-- Rótulo / Badge auxiliar (ex: >20d) -->
            <span
              v-if="opt.badgeText"
              class="text-[10px] text-gray-400 font-normal ml-auto shrink-0"
            >
              {{ opt.badgeText }}
            </span>
          </label>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

export interface DropdownOption {
  label: string;
  value: string;
  colorClass?: string;
  badgeText?: string;
}

const props = defineProps<{
  label: string;
  options: DropdownOption[];
  modelValue: string[];
  placeholder?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: string[]): void;
  (e: 'change', val: string[]): void;
}>();

const isOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

const selectedCount = computed(() => props.modelValue.length);

const isSelected = (val: string) => props.modelValue.includes(val);

const displaySummary = computed(() => {
  if (props.modelValue.length === 0) return '';
  const firstMatch = props.options.find(o => o.value === props.modelValue[0]);
  return firstMatch ? firstMatch.label : props.modelValue[0];
});

function toggleOption(val: string) {
  let updated = [...props.modelValue];
  if (updated.includes(val)) {
    updated = updated.filter(v => v !== val);
  } else {
    updated.push(val);
  }
  emit('update:modelValue', updated);
  emit('change', updated);
}

function selectAll() {
  const all = props.options.map(o => o.value);
  emit('update:modelValue', all);
  emit('change', all);
}

function clearAll() {
  emit('update:modelValue', []);
  emit('change', []);
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
