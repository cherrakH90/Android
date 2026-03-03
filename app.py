
import os
from flask import Flask, render_template_string

app = Flask(__name__)

# [TITAN ENGINE V100 - THE FINAL REPLICA]
HTML_CONTENT = r'''
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CHERRAK V100 | TITAN SHARK</title>
    <style>
        :root { --neon: #00f2ff; --glass: rgba(0, 30, 60, 0.5); --gold: #ffd700; }
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; touch-action: none; }
        
        body { 
            background: #000; overflow: hidden; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            height: 100vh; color: #fff; 
        }

        /* خلفية المحيط العميقة */
        #ocean-bg {
            position: fixed; inset: 0;
            background: radial-gradient(circle at 50% 40%, #004d7a 0%, #00081a 100%);
            z-index: -2;
        }

        canvas { display: block; filter: saturate(1.5) contrast(1.2); }

        /* HUD - الواجهة الاحترافية الزجاجية */
        .hud { position: absolute; inset: 0; padding: 35px 25px; pointer-events: none; }
        
        .header { margin-bottom: 35px; }
        .main-score { 
            font-size: 45px; font-weight: 900; color: var(--neon); 
            text-shadow: 0 0 20px rgba(0, 242, 255, 0.6);
            display: flex; align-items: center; gap: 10px;
        }
        .sub-title { font-size: 13px; letter-spacing: 3px; opacity: 0.8; text-transform: uppercase; margin-top: 5px; }

        .stats-grid { display: flex; flex-direction: column; gap: 15px; width: 230px; }
        .glass-card {
            background: var(--glass); border: 1px solid rgba(0, 242, 255, 0.25);
            padding: 18px; border-radius: 15px; backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .card-label { font-size: 10px; letter-spacing: 1.5px; opacity: 0.6; text-transform: uppercase; margin-bottom: 8px; }
        .card-value { font-size: 26px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
        
        .bar-container { width: 100%; height: 5px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; margin-top: 12px; overflow: hidden; }
        .bar-fill { height: 100%; background: var(--neon); box-shadow: 0 0 12px var(--neon); transition: 0.4s cubic-bezier(0.17, 0.67, 0.83, 0.67); }

        .btn-restart {
            margin-top: 20px; width: 100%; padding: 15px; background: rgba(0, 242, 255, 0.1);
            border: 2px solid var(--neon); color: var(--neon); font-weight: bold;
            border-radius: 10px; pointer-events: auto; cursor: pointer; text-transform: uppercase;
        }

        /* شاشة الفوز النهائية */
        #victory-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.95);
            display: none; flex-direction: column; align-items: center; justify-content: center;
            z-index: 1000; text-align: center; pointer-events: auto;
        }
        .trophy-anim { font-size: 130px; filter: drop-shadow(0 0 30px var(--gold)); animation: float 3s ease-in-out infinite; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
    </style>
</head>
<body>
    <div id="ocean-bg"></div>
    
    <div id="victory-overlay">
        <div class="trophy-anim">🏆</div>
        <h1 style="color:var(--gold); font-size: 50px; margin-top: 20px;">KING OF THE OCEAN</h1>
        <p style="font-size: 24px; margin: 20px; color: #fff;">لقد حصلت على الكنز: 💰 1,000,000</p>
        <button class="btn-restart" onclick="location.reload()" style="width: 250px;">العب مجدداً</button>
    </div>

    <canvas id="gameCanvas"></canvas>

    <div class="hud">
        <div class="header">
            <div class="main-score"><span id="score-val">300000</span> Cherrak 🦈🏆🌕</div>
            <div class="sub-title">CHERRAK | BLUE GLOW OVERLORD</div>
        </div>

        <div class="stats-grid">
            <div class="glass-card">
                <div class="card-label">Depth Level (المرحلة)</div>
                <div class="card-value" id="lvl-txt">01 / 07</div>
                <div class="bar-container"><div class="bar-fill" id="lvl-bar" style="width: 14%"></div></div>
            </div>

            <div class="glass-card">
                <div class="card-label">Fish Eaten (التقدم)</div>
                <div class="card-value"><span id="eat-val">0</span> <small style="font-size:14px; opacity:0.5;">/ 100</small></div>
                <div class="bar-container"><div class="bar-fill" id="eat-bar" style="width: 0%"></div></div>
            </div>

            <div class="glass-card">
                <div class="card-label">Revenue (الأرباح)</div>
                <div class="card-value" id="rev-val">$5000</div>
            </div>

            <div class="btn-restart" onclick="location.reload()">Restart System</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas'), ctx = canvas.getContext('2d');
        let w, h, score = 300000, revenue = 5000, eaten = 0, level = 1, shake = 0;
        const mouse = { x: 0, y: 0 };

        function resize() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
            mouse.x = w/2; mouse.y = h/2;
        }
        window.onresize = resize;
        window.onmousemove = e => { mouse.x = e.clientX; mouse.y = e.clientY; };
        window.ontouchmove = e => { mouse.x = e.touches[0].clientX; mouse.y = e.touches[0].clientY; };
        resize();

        class Shark {
            constructor() {
                this.parts = Array.from({length: 14}, (_, i) => ({ x: w/2, y: h/2, r: 50 - i*3.2, a: 0 }));
            }
            update() {
                let head = this.parts[0];
                head.x += (mouse.x - head.x) * 0.16;
                head.y += (mouse.y - head.y) * 0.16;
                head.a = Math.atan2(mouse.y - head.y, mouse.x - head.x);

                for(let i=1; i<this.parts.length; i++) {
                    let p = this.parts[i-1], c = this.parts[i];
                    let ang = Math.atan2(p.y - c.y, p.x - c.x);
                    c.a = ang;
                    c.x = p.x - Math.cos(ang) * 16;
                    c.y = p.y - Math.sin(ang) * 16;
                }
            }
            draw() {
                this.parts.forEach((p, i) => {
                    ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a);
                    ctx.shadowBlur = 35; ctx.shadowColor = '#00f2ff';
                    ctx.fillStyle = i === 0 ? '#fff' : `rgba(0, 242, 255, ${1 - i/14})`;
                    
                    ctx.beginPath();
                    if(i === 0) { // الرأس الاحترافي
                        ctx.ellipse(0, 0, p.r, p.r*0.7, 0, 0, Math.PI*2); ctx.fill();
                        ctx.fillStyle = 'red'; ctx.beginPath(); ctx.arc(18, -12, 5, 0, 7); ctx.fill();
                        ctx.beginPath(); ctx.arc(18, 12, 5, 0, 7); ctx.fill();
                        // زعانف الصدر
                        ctx.fillStyle = 'rgba(0, 242, 255, 0.8)';
                        ctx.beginPath(); ctx.moveTo(0, -20); ctx.lineTo(-25, -60); ctx.lineTo(-10, -15); ctx.fill();
                        ctx.beginPath(); ctx.moveTo(0, 20); ctx.lineTo(-25, 60); ctx.lineTo(-10, 15); ctx.fill();
                    } else if(i === 6) { // الزعنفة الظهرية
                        ctx.ellipse(0, 0, p.r, p.r*0.6, 0, 0, Math.PI*2); ctx.fill();
                        ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-35, -45); ctx.lineTo(-15, 0); ctx.fill();
                    } else {
                        ctx.ellipse(0, 0, p.r, p.r*0.6, 0, 0, Math.PI*2); ctx.fill();
                    }
                    ctx.restore();
                });
            }
        }

        class Fish {
            constructor() { this.init(); }
            init() {
                this.x = Math.random()*w; this.y = Math.random()*h;
                this.v = 1.8 + (level * 0.4);
                this.ang = Math.random()*7;
                this.emoji = ["🐟", "🐠", "🐡"][Math.floor(Math.random()*3)];
                this.size = 50 + Math.random()*20; // حجم ضخم كما طلبت
                this.dead = false;
            }
            update(sh) {
                if(this.dead) return;
                let dx = this.x - sh.parts[0].x, dy = this.y - sh.parts[0].y;
                let d = Math.sqrt(dx*dx + dy*dy);
                
                if(d < 160) { this.ang = Math.atan2(dy, dx); this.v = 5.5; } // AI الهروب
                
                this.x += Math.cos(this.ang)*this.v;
                this.y += Math.sin(this.ang)*this.v;
                
                if(this.x<0||this.x>w||this.y<0||this.y>h) this.init();

                if(d < 60) { // حدث الأكل
                    this.dead = true;
                    eaten++; revenue += (level * 150);
                    shake = 15; // اهتزاز الشاشة
                    updateHUD();
                    setTimeout(() => this.init(), 500);
                }
            }
            draw() {
                if(this.dead) return;
                ctx.font = `${this.size}px Arial`;
                ctx.fillText(this.emoji, this.x, this.y);
            }
        }

        function updateHUD() {
            document.getElementById('eat-val').innerText = eaten;
            document.getElementById('eat-bar').style.width = eaten + '%';
            document.getElementById('rev-val').innerText = '$' + revenue;

            if(eaten >= 100) {
                if(level < 7) {
                    level++; eaten = 0;
                    document.getElementById('lvl-txt').innerText = `0${level} / 07`;
                    document.getElementById('lvl-bar').style.width = (level/7 * 100) + '%';
                    alert(`LEVEL ${level} UNLOCKED!`);
                } else {
                    document.getElementById('victory-overlay').style.display = 'flex';
                }
            }
        }

        const shark = new Shark();
        const fishes = Array.from({length: 15}, () => new Fish());

        function loop() {
            ctx.clearRect(0, 0, w, h);
            
            if(shake > 0) {
                ctx.save();
                ctx.translate(Math.random()*shake-shake/2, Math.random()*shake-shake/2);
                shake *= 0.9;
            }

            fishes.forEach(f => { f.update(shark); f.draw(); });
            shark.update(); shark.draw();

            if(shake > 0.1) ctx.restore();
            requestAnimationFrame(loop);
        }
        loop();
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    print("\n🔱 CHERRAK V100 OVERLORD STARTED ON PORT 7000")
    app.run(host='0.0.0.0', port=7000, threaded=True)

