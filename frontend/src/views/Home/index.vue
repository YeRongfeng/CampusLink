<script setup lang="ts">
import { NButton } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import ModuleCard from '../../components/common/ModuleCard.vue'
import { useAuthStore } from '../../stores/auth'
const auth = useAuthStore()
</script>
<template>
  <AppContainer>
    <main class="home-page">
      <section class="home-hero">
        <div class="hero-copy">
          <p class="eyebrow">CAMPUSLINK · 校园生活连接站</p>
          <h1>校园很大，<br />让彼此<span>更近一点。</span></h1>
          <p class="hero-description">一起出发，搭一把手，让好书继续流转。<br class="hidden sm:block" />你的校园日常，总有人同频。</p>
          <div class="hero-actions">
            <RouterLink :to="auth.isAuthenticated ? '/profile' : '/register'"><NButton type="primary" size="large">{{ auth.isAuthenticated ? '我的 CampusLink' : '加入 CampusLink' }}</NButton></RouterLink>
            <a href="#campus-services" class="quiet-link">探索校园服务</a>
          </div>
        </div>
        <aside class="hero-note">
          <p class="eyebrow">BETTER TOGETHER</p>
          <h2>美好的校园生活，<br />从一次连接开始。</h2>
          <div class="note-line"><span>同行</span><p>同一个目的地，多一份陪伴。</p></div>
          <div class="note-line"><span>互助</span><p>你的小需要，同学的举手之劳。</p></div>
          <div class="note-line"><span>分享</span><p>读过的好书，遇见新的主人。</p></div>
          <p class="note-footer">在这里，遇见校园里的更多可能。</p>
        </aside>
      </section>
      <section id="campus-services" class="services-section" aria-labelledby="services-title">
        <div class="section-heading"><div><p class="eyebrow">EXPLORE CAMPUS</p><h2 id="services-title">从这里，连接你的日常</h2></div><p>三种方式，让校园生活更轻松。</p></div>
        <div class="grid gap-6 md:grid-cols-3">
          <ModuleCard title="校园拼车" description="找到与你同行的人，让每一段出发都有伴。" to="/ride" label="CAMPUS RIDE" number="01" />
          <ModuleCard title="校园悬赏" description="让顺手的人帮你解决小事，让互助发生在身边。" to="/quest" label="CAMPUS QUEST" number="02" />
          <ModuleCard title="二手书" description="让闲置教材继续流转，把知识传给下一位同学。" to="/book" label="CAMPUS BOOK" number="03" />
        </div>
      </section>
      <footer class="home-footer"><strong>CampusLink</strong><p>连接同学，连接校园里的每一种可能。</p><span>同行 · 互助 · 分享</span></footer>
    </main>
  </AppContainer>
</template>
