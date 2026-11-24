<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  options: {
    type: Array,
    required: true,
    // Expected items: { value, label, subtitle?, color?, icon? }
  },
  placeholder: {
    type: String,
    default: 'Pilih opsi...',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const selectRef = ref(null)

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === props.modelValue) || null
})

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

function selectOption(opt) {
  emit('update:modelValue', opt.value)
  isOpen.value = false
}

function handleClickOutside(e) {
  if (selectRef.value && !selectRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="selectRef" class="relative w-full text-xs">
    <!-- Trigger Button -->
    <button
      type="button"
      @click="toggleDropdown"
      :disabled="disabled"
      class="w-full flex items-center justify-between gap-2 px-3 py-2 text-left bg-white border rounded-xl shadow-2xs transition-all cursor-pointer focus:outline-hidden"
      :class="[
        isOpen
          ? 'border-indigo-500 ring-2 ring-indigo-500/20'
          : 'border-slate-300 hover:border-slate-400',
        disabled ? 'bg-slate-50 opacity-60 cursor-not-allowed' : '',
      ]"
    >
      <div class="flex items-center gap-2 min-w-0 truncate">
        <!-- Color dot if option has color -->
        <span
          v-if="selectedOption?.color"
          class="w-2.5 h-2.5 rounded-full shrink-0"
          :style="{ backgroundColor: selectedOption.color }"
        ></span>

        <!-- Component icon if provided -->
        <component
          :is="selectedOption.icon"
          v-if="selectedOption?.icon"
          class="w-3.5 h-3.5 text-slate-500 shrink-0"
        />

        <span
          v-if="selectedOption"
          class="font-semibold text-slate-800 truncate"
        >
          {{ selectedOption.label }}
          <span v-if="selectedOption.subtitle" class="text-slate-400 font-normal ml-1">
            ({{ selectedOption.subtitle }})
          </span>
        </span>
        <span v-else class="text-slate-400 font-normal truncate">
          {{ placeholder }}
        </span>
      </div>

      <ChevronDown
        class="w-4 h-4 text-slate-400 shrink-0 transition-transform duration-200"
        :class="{ 'rotate-180 text-indigo-500': isOpen }"
      />
    </button>

    <!-- Dropdown Menu -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="transform opacity-0 scale-95 -translate-y-1"
      enter-to-class="transform opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform opacity-100 scale-100 translate-y-0"
      leave-to-class="transform opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute left-0 right-0 z-50 mt-1 max-h-56 overflow-y-auto rounded-xl bg-white border border-slate-200 shadow-xl p-1 space-y-0.5"
      >
        <button
          v-for="opt in options"
          :key="opt.value"
          type="button"
          @click="selectOption(opt)"
          class="w-full flex items-center justify-between px-2.5 py-2 text-left rounded-lg transition-colors cursor-pointer group"
          :class="[
            opt.value === modelValue
              ? 'bg-indigo-50/80 text-indigo-900 font-semibold'
              : 'text-slate-700 hover:bg-slate-100 font-medium',
          ]"
        >
          <div class="flex items-center gap-2 min-w-0 truncate">
            <span
              v-if="opt.color"
              class="w-2.5 h-2.5 rounded-full shrink-0"
              :style="{ backgroundColor: opt.color }"
            ></span>
            <component
              :is="opt.icon"
              v-if="opt.icon"
              class="w-3.5 h-3.5 text-slate-500 shrink-0"
            />
            <span class="truncate">{{ opt.label }}</span>
            <span
              v-if="opt.subtitle"
              class="text-[11px] text-slate-400 font-normal truncate"
            >
              {{ opt.subtitle }}
            </span>
          </div>

          <Check
            v-if="opt.value === modelValue"
            class="w-3.5 h-3.5 text-indigo-600 shrink-0 ml-2"
          />
        </button>

        <div
          v-if="options.length === 0"
          class="px-3 py-3 text-center text-slate-400 text-xs italic"
        >
          Tidak ada opsi tersedia
        </div>
      </div>
    </Transition>
  </div>
</template>
