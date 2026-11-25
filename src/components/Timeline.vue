<template>
  <div class="timeline-wrap">
    <div class="timeline-header">
      <h2>{{ storyline.title }} · 时间轴</h2>
      <span class="count">{{ storyline.events.length }} 个事件</span>
    </div>

    <div v-if="storyline.events.length === 0" class="empty">
      还没有事件，添加事件后这里会出现时间轴。
    </div>

    <div v-else class="timeline" ref="timelineEl">
      <!-- SVG 主线：描边动画画出来 -->
      <svg class="track" preserveAspectRatio="none">
        <line x1="0" y1="0" x2="0" y2="100%" class="track-line" />
      </svg>

      <!-- 事件节点：逐个淡入 -->
      <div
        v-for="(event, index) in storyline.events"
        :key="event.id"
        class="node"
        :style="{ animationDelay: (index * 0.12) + 's' }"
        @click="openDetail(event)"
      >
        <div class="node-dot" :class="dotClass(event)"></div>
        <div class="node-card">
          <div class="node-date">{{ event.date || '未设日期' }}</div>
          <div class="node-title">{{ event.title }}</div>
          <div class="node-people">
            <span v-for="p in event.people" :key="p" class="people-chip" :class="'chip-' + p">
              {{ personName(p) }}
            </span>
          </div>
          <img v-if="event.imageUrl" :src="event.imageUrl" class="node-img" alt="配图" />
        </div>
      </div>
    </div>

    <!-- 事件详情弹窗 -->
    <div v-if="detail" class="modal-mask" @click.self="closeDetail">
      <div class="modal">
        <button class="modal-close" @click="closeDetail">×</button>
        <div class="modal-date">{{ detail.date || '未设日期' }}</div>
        <h3 class="modal-title">{{ detail.title }}</h3>
        <div class="modal-people">
          <span v-for="p in detail.people" :key="p" class="people-chip" :class="'chip-' + p">
            {{ personName(p) }}
          </span>
        </div>
        <div class="modal-tags">
          <span v-for="t in detail.tags" :key="t">#{{ t }}</span>
        </div>
        <img v-if="detail.imageUrl" :src="detail.imageUrl" class="modal-img" alt="事件配图" />
        <p class="modal-desc">{{ detail.description || '（无描述）' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  storyline: {
    type: Object,
    required: true,
  },
})

const detail = ref(null)

// 'A'/'B' 代号映射成真名（与 EventEditor 同一约定）
function personName(code) {
  if (code === 'A') return props.storyline.personA || 'A'
  if (code === 'B') return props.storyline.personB || 'B'
  return code
}

// 节点颜色按参与者区分：两人=紫，A=蓝，B=粉
function dotClass(event) {
  if (event.people.includes('A') && event.people.includes('B')) return 'dot-both'
  if (event.people.includes('A')) return 'dot-a'
  if (event.people.includes('B')) return 'dot-b'
  return 'dot-both'
}

function openDetail(event) {
  detail.value = event
}

function closeDetail() {
  detail.value = null
}
</script>

<style scoped>
.timeline-wrap {
  min-width: 0;
}
.timeline-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 20px;
}
h2 {
  font-size: 17px;
  font-weight: 500;
  margin: 0;
}
.count {
  font-size: 12px;
  color: #999;
}
.empty {
  color: #999;
  font-size: 13px;
  padding: 40px 0;
  text-align: center;
}
.timeline {
  position: relative;
  padding-left: 32px;
}
.track {
  position: absolute;
  left: 7px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  overflow: visible;
}
.track-line {
  stroke: #d8d8d8;
  stroke-width: 2;
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawLine 1.2s ease-out forwards;
}
@keyframes drawLine {
  to { stroke-dashoffset: 0; }
}
.node {
  position: relative;
  margin-bottom: 20px;
  opacity: 0;
  transform: translateY(12px);
  animation: nodeIn 0.5s ease-out forwards;
  cursor: pointer;
}
@keyframes nodeIn {
  to { opacity: 1; transform: translateY(0); }
}
.node-dot {
  position: absolute;
  left: -32px;
  top: 12px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #ddd;
  transition: transform 0.2s;
}
.node:hover .node-dot {
  transform: scale(1.3);
}
.dot-both { background: #7c5cbf; box-shadow: 0 0 0 2px #7c5cbf; }
.dot-a { background: #409eff; box-shadow: 0 0 0 2px #409eff; }
.dot-b { background: #e591b6; box-shadow: 0 0 0 2px #e591b6; }
.node-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 12px 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.node:hover .node-card {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}
.node-date {
  font-size: 12px;
  color: #999;
}
.node-title {
  font-size: 15px;
  font-weight: 500;
  margin: 2px 0 6px;
}
.node-people, .modal-people {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.people-chip {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}
.chip-A { background: #e8f4ff; color: #409eff; }
.chip-B { background: #fdeef5; color: #d06a9c; }
.node-img {
  width: 100%;
  max-height: 100px;
  object-fit: cover;
  border-radius: 6px;
  margin-top: 8px;
}
.modal-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal {
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: min(90vw, 480px);
  max-height: 85vh;
  overflow-y: auto;
  animation: modalIn 0.3s cubic-bezier(0.2, 0.9, 0.3, 1.2);
}
@keyframes modalIn {
  from { opacity: 0; transform: scale(0.9) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 30px;
  height: 30px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  font-size: 18px;
  color: #666;
  cursor: pointer;
  line-height: 1;
}
.modal-date {
  font-size: 13px;
  color: #999;
}
.modal-title {
  font-size: 20px;
  font-weight: 500;
  margin: 6px 0 10px;
}
.modal-tags {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  color: #999;
  font-size: 12px;
}
.modal-img {
  width: 100%;
  border-radius: 8px;
  margin-top: 14px;
}
.modal-desc {
  font-size: 14px;
  line-height: 1.7;
  margin-top: 14px;
  color: #444;
  white-space: pre-wrap;
}
</style>
