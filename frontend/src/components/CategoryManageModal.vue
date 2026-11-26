<script setup>
import { ref } from 'vue'
import { useBoardStore } from '../stores/boardStore'
import { formatRupiah } from '../utils/formatters'
import ConfirmModal from './ui/ConfirmModal.vue'
import {
  Tag,
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  AlertCircle,
  HelpCircle,
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const boardStore = useBoardStore()

const showAddForm = ref(false)
const newCategoryForm = ref({
  name: '',
  monthly_budget: '0',
  color: '#3B82F6',
})
const isAdding = ref(false)
const errorMessage = ref('')

// Predefined palette colors
const presetColors = [
  '#EF4444', // Red
  '#F59E0B', // Amber
  '#10B981', // Emerald
  '#3B82F6', // Blue
  '#6366F1', // Indigo
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
]

// Editing state
const editingCategoryId = ref(null)
const editForm = ref({
  name: '',
  monthly_budget: '',
  color: '#3B82F6',
})
const isSavingEdit = ref(false)

// Delete confirm dialog
const isConfirmOpen = ref(false)
const categoryToDelete = ref(null)

function startEdit(cat) {
  editingCategoryId.value = cat.id
  editForm.value = {
    name: cat.name,
    monthly_budget: String(cat.monthly_budget || '0'),
    color: cat.color || '#3B82F6',
  }
}

function cancelEdit() {
  editingCategoryId.value = null
  editForm.value = { name: '', monthly_budget: '', color: '#3B82F6' }
}

async function saveEdit(catId) {
  if (!editForm.value.name.trim()) return
  isSavingEdit.value = true
  errorMessage.value = ''
  try {
    await boardStore.updateCategory(catId, {
      name: editForm.value.name.trim(),
      monthly_budget: Number(editForm.value.monthly_budget || 0).toFixed(2),
      color: editForm.value.color,
    })
    cancelEdit()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memperbarui kategori.'
  } finally {
    isSavingEdit.value = false
  }
}

async function handleAddCategory() {
  if (!newCategoryForm.value.name.trim()) {
    errorMessage.value = 'Nama kategori wajib diisi.'
    return
  }
  isAdding.value = true
  errorMessage.value = ''
  try {
    await boardStore.createCategory({
      name: newCategoryForm.value.name.trim(),
      monthly_budget: Number(newCategoryForm.value.monthly_budget || 0).toFixed(2),
      color: newCategoryForm.value.color,
    })
    newCategoryForm.value = { name: '', monthly_budget: '0', color: '#3B82F6' }
    showAddForm.value = false
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menambahkan kategori.'
  } finally {
    isAdding.value = false
  }
}

function promptDelete(cat) {
  categoryToDelete.value = cat
  isConfirmOpen.value = true
}

async function executeDelete() {
  if (!categoryToDelete.value) return
  isConfirmOpen.value = false
  errorMessage.value = ''
  try {
    await boardStore.deleteCategory(categoryToDelete.value.id)
    categoryToDelete.value = null
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menghapus kategori.'
  }
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
        @click="emit('close')"
      ></div>

      <div class="flex min-h-full items-center justify-center p-4">
        <!-- Modal Card with scale transition -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-2"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 translate-y-2"
        >
          <div
            class="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200"
          >
            <!-- Modal Header -->
            <div class="flex items-center justify-between pb-4 border-b border-slate-100">
              <div class="flex items-center gap-2.5">
                <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center">
                  <Tag class="w-5 h-5" />
                </div>
                <div>
                  <h2 class="text-base font-bold text-slate-800">Kelola Kategori & Budget</h2>
                  <p class="text-xs text-slate-500">Atur kategori pengeluaran dan batas anggaran bulanan</p>
                </div>
              </div>
              <button
                @click="emit('close')"
                class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Error Alert -->
            <div
              v-if="errorMessage"
              class="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2"
            >
              <AlertCircle class="w-4 h-4 shrink-0" />
              <span>{{ errorMessage }}</span>
            </div>

            <!-- Add Form Toggle -->
            <div class="mt-4 flex items-center justify-between">
              <span class="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Daftar Kategori ({{ boardStore.categories.length }})
              </span>
              <button
                @click="showAddForm = !showAddForm"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors cursor-pointer"
              >
                <Plus class="w-3.5 h-3.5" />
                <span>{{ showAddForm ? 'Tutup Form' : 'Tambah Kategori' }}</span>
              </button>
            </div>

            <!-- Inline Add Category Form -->
            <div
              v-if="showAddForm"
              class="mt-3 p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3"
            >
              <div class="text-xs font-semibold text-slate-800">Form Kategori Baru:</div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <input
                  v-model="newCategoryForm.name"
                  type="text"
                  placeholder="Nama Kategori (Makanan, Utilitas, dll)"
                  class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white font-medium"
                />
                <input
                  v-model="newCategoryForm.monthly_budget"
                  type="number"
                  min="0"
                  step="any"
                  placeholder="Batas Budget Bulanan (Rp)"
                  class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white font-bold"
                />
              </div>

              <!-- Color Picker Presets -->
              <div class="flex items-center gap-2 pt-1">
                <span class="text-xs text-slate-500 font-medium">Warna Label:</span>
                <div class="flex items-center gap-1.5">
                  <button
                    v-for="color in presetColors"
                    :key="color"
                    type="button"
                    @click="newCategoryForm.color = color"
                    class="w-5 h-5 rounded-full transition-transform cursor-pointer"
                    :class="newCategoryForm.color === color ? 'ring-2 ring-slate-800 scale-110' : 'hover:scale-105'"
                    :style="{ backgroundColor: color }"
                  ></button>
                </div>
              </div>

              <div class="flex justify-end gap-2 pt-1">
                <button
                  @click="showAddForm = false"
                  class="px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-200 rounded-lg"
                >
                  Batal
                </button>
                <button
                  @click="handleAddCategory"
                  :disabled="isAdding"
                  class="px-4 py-1 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-lg shadow-2xs disabled:opacity-50"
                >
                  {{ isAdding ? 'Menyimpan...' : 'Simpan Kategori' }}
                </button>
              </div>
            </div>

            <!-- Categories List -->
            <div class="mt-3 space-y-2 max-h-64 overflow-y-auto pr-1">
              <div
                v-for="cat in boardStore.categories"
                :key="cat.id"
                class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white shadow-2xs transition-all hover:border-slate-300"
              >
                <!-- View Mode -->
                <template v-if="editingCategoryId !== cat.id">
                  <div class="flex items-center gap-3">
                    <span
                      class="w-3.5 h-3.5 rounded-full shrink-0"
                      :style="{ backgroundColor: cat.color }"
                    ></span>
                    <div>
                      <h4 class="text-xs font-bold text-slate-800">{{ cat.name }}</h4>
                      <p class="text-[11px] text-slate-500 font-medium">
                        Budget: {{ formatRupiah(cat.monthly_budget) }} / bln
                      </p>
                    </div>
                  </div>

                  <div class="flex items-center gap-1.5">
                    <button
                      @click="startEdit(cat)"
                      class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors cursor-pointer"
                    >
                      <Edit2 class="w-3.5 h-3.5" />
                    </button>
                    <button
                      @click="promptDelete(cat)"
                      class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </template>

                <!-- Edit Mode -->
                <template v-else>
                  <div class="flex-1 space-y-2 mr-2">
                    <div class="grid grid-cols-2 gap-2">
                      <input
                        v-model="editForm.name"
                        type="text"
                        class="px-2.5 py-1 text-xs rounded-lg border border-slate-300 font-medium"
                      />
                      <input
                        v-model="editForm.monthly_budget"
                        type="number"
                        class="px-2.5 py-1 text-xs rounded-lg border border-slate-300 font-bold"
                      />
                    </div>
                    <!-- Color picker presets for edit -->
                    <div class="flex items-center gap-1.5">
                      <button
                        v-for="color in presetColors"
                        :key="color"
                        type="button"
                        @click="editForm.color = color"
                        class="w-4 h-4 rounded-full transition-transform cursor-pointer"
                        :class="editForm.color === color ? 'ring-2 ring-slate-800 scale-110' : ''"
                        :style="{ backgroundColor: color }"
                      ></button>
                    </div>
                  </div>

                  <div class="flex items-center gap-1 shrink-0">
                    <button
                      @click="saveEdit(cat.id)"
                      :disabled="isSavingEdit"
                      class="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg cursor-pointer"
                    >
                      <Check class="w-4 h-4 stroke-[2.5]" />
                    </button>
                    <button
                      @click="cancelEdit"
                      class="p-1.5 text-slate-400 hover:bg-slate-100 rounded-lg cursor-pointer"
                    >
                      <X class="w-4 h-4" />
                    </button>
                  </div>
                </template>
              </div>

              <!-- Empty state -->
              <div
                v-if="boardStore.categories.length === 0"
                class="p-8 text-center text-xs text-slate-400 border-2 border-dashed border-slate-200 rounded-xl"
              >
                <HelpCircle class="w-6 h-6 mx-auto mb-2 text-slate-300" />
                <span>Belum ada kategori. Klik "+ Tambah Kategori" di atas.</span>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Confirm Delete Modal -->
      <ConfirmModal
        :is-open="isConfirmOpen"
        :title="`Hapus Kategori '${categoryToDelete?.name}'?`"
        :message="`Apakah Anda yakin ingin menghapus kategori '${categoryToDelete?.name}'? Kartu dengan kategori ini tidak akan dihapus, melainkan diubah menjadi tanpa kategori.`"
        confirm-text="Hapus Kategori"
        cancel-text="Batal"
        :is-danger="true"
        @confirm="executeDelete"
        @cancel="isConfirmOpen = false"
      />
    </div>
  </Transition>
</template>
