export function formatRupiah(value, isPrivacy = false) {
  if (isPrivacy) {
    return 'Rp ••••••••'
  }
  if (value === null || value === undefined || isNaN(value)) {
    return 'Rp 0'
  }
  const number = Number(value)
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(number)
}

export function formatDate(dateString) {
  if (!dateString) return null
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

export function getDueDateUrgency(dueDateStr, isPaid = false) {
  if (isPaid) {
    return {
      type: 'paid',
      label: 'Lunas',
      badgeClass: 'text-emerald-700 bg-emerald-50 border-emerald-200',
    }
  }
  if (!dueDateStr) return null

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const due = new Date(dueDateStr)
  due.setHours(0, 0, 0, 0)

  const diffTime = due.getTime() - today.getTime()
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return {
      type: 'overdue',
      label: `Lewat ${Math.abs(diffDays)} hari!`,
      badgeClass: 'text-rose-700 bg-rose-50 border-rose-300 font-bold animate-pulse',
      isOverdue: true,
    }
  }
  if (diffDays === 0) {
    return {
      type: 'today',
      label: 'Jatuh tempo hari ini!',
      badgeClass: 'text-rose-600 bg-rose-50 border-rose-200 font-bold',
      isToday: true,
    }
  }
  if (diffDays <= 3) {
    return {
      type: 'soon',
      label: `${diffDays} hari lagi`,
      badgeClass: 'text-amber-700 bg-amber-50 border-amber-200 font-semibold',
      isSoon: true,
    }
  }
  return {
    type: 'normal',
    label: formatDate(dueDateStr),
    badgeClass: 'text-slate-600 bg-slate-100 border-slate-200',
  }
}
