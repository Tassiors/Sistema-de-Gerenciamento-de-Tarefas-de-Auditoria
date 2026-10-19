<template>
  <teleport to="body">
    <!-- Overlay com Blur -->
    <transition name="fade">
      <div 
        v-if="isVisible" 
        class="fixed inset-0 bg-gray-900/60 backdrop-blur-xs z-40 transition-opacity" 
        @click="close"
      ></div>
    </transition>

    <!-- Container do Modal -->
    <transition name="modal-scale">
      <div 
        v-if="isVisible" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto"
        @click.self="close"
      >
        <div 
          class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col overflow-hidden transform transition-all my-auto"
          @click.stop
        >
          <!-- Header -->
          <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/70 shrink-0">
            <h2 class="text-base font-bold text-gray-900">
              <slot name="header">{{ title || 'Título do Modal' }}</slot>
            </h2>
            <button 
              type="button"
              @click="close" 
              class="p-1.5 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-200/60 transition-colors cursor-pointer"
              title="Fechar (Esc)"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>

          <!-- Body -->
          <div class="px-6 py-5 text-gray-700 overflow-y-auto flex-1 text-xs">
            <slot></slot>
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="px-6 py-3.5 border-t border-gray-100 bg-gray-50/70 flex justify-end space-x-2 shrink-0">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { XMarkIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  show: { type: Boolean, default: false },
  isOpen: { type: Boolean, default: false },
  title: { type: String, default: '' },
});

const emit = defineEmits(['close']);
const close = () => emit('close');

const isVisible = computed(() => props.show || props.isOpen);

// Bloqueia o scroll do corpo quando o modal abre
watch(isVisible, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

const handleEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && isVisible.value) close();
};

onMounted(() => document.addEventListener('keydown', handleEscape));
onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape);
  document.body.style.overflow = '';
});
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.modal-scale-enter-active { transition: all 0.25s ease-out; }
.modal-scale-leave-active { transition: all 0.15s ease-in; }
.modal-scale-enter-from { opacity: 0; transform: scale(0.96) translateY(-8px); }
.modal-scale-leave-to { opacity: 0; transform: scale(0.96) translateY(8px); }
</style>
