var c = document.getElementById( 'c' );
var gl = c.getContext( 'webgl', { preserveDrawingBuffer: true } )
	,	w = c.width = window.innerWidth
	,	h = c.height = window.innerHeight

	,	webgl = {}
	,	opts = {
		projectileAlpha: .9,
		projectileLineWidth: 2,
		fireworkAngleSpan: .9,
		baseFireworkVel: 4,
		addedFireworkVel: 2,
		gravity: .03,
		lowVelBoundary: -.2,
		xFriction: .995,
		baseShardVel: 1,
		addedShardVel: .2,
		fireworks: 50,
		baseShardsParFirework: 6,
		addedShardsParFirework: 6,
		shardTrailLength: 15,
		shardTTL: 70,
		shardFireworkVelMultiplier: .6,
		initHueMultiplier: 1/360,
		runHueAdder: .1/360
	}

webgl.vertexShaderSource = `
uniform int u_mode;
uniform vec2 u_res;
attribute vec4 a_data;
varying vec4 v_color;

vec3 h2rgb( float h ){
	return clamp( abs( mod( h * 6. + vec3( 0, 4, 2 ), 6. ) - 3. ) -1., 0., 1. );
}
void clear(){
	gl_Position = vec4( a_data.xy, 0, 1 );
	v_color = vec4( 0, 0, 0, a_data.w );
}
void draw(){
	gl_Position = vec4( vec2( 1, -1 ) * ( ( a_data.xy / u_res ) * 2. - 1. ), 0, 1 );
	v_color = vec4( h2rgb( a_data.z ), a_data.w );
}
void main(){
	if( u_mode == 0 )
		draw();
	else
		clear();
}
`;
webgl.fragmentShaderSource = `
precision mediump float;
varying vec4 v_color;

void main(){
	gl_FragColor = v_color;
}
`;

webgl.vertexShader = gl.createShader( gl.VERTEX_SHADER );
gl.shaderSource( webgl.vertexShader, webgl.vertexShaderSource );
gl.compileShader( webgl.vertexShader );

webgl.fragmentShader = gl.createShader( gl.FRAGMENT_SHADER );
gl.shaderSource( webgl.fragmentShader, webgl.fragmentShaderSource );
gl.compileShader( webgl.fragmentShader );

webgl.shaderProgram = gl.createProgram();
gl.attachShader( webgl.shaderProgram, webgl.vertexShader );
gl.attachShader( webgl.shaderProgram, webgl.fragmentShader );

gl.linkProgram( webgl.shaderProgram );
gl.useProgram( webgl.shaderProgram );

webgl.dataAttribLoc = gl.getAttribLocation( webgl.shaderProgram, 'a_data' );
webgl.dataBuffer = gl.createBuffer();

gl.enableVertexAttribArray( webgl.dataAttribLoc );
gl.bindBuffer( gl.ARRAY_BUFFER, webgl.dataBuffer );
gl.vertexAttribPointer( webgl.dataAttribLoc, 4, gl.FLOAT, false, 0, 0 );

webgl.resUniformLoc = gl.getUniformLocation( webgl.shaderProgram, 'u_res' );
webgl.modeUniformLoc = gl.getUniformLocation( webgl.shaderProgram, 'u_mode' );

gl.viewport( 0, 0, w, h );
gl.uniform2f( webgl.resUniformLoc, w, h );
gl.uniform1i( webgl.modeUniformLoc, 0 );

gl.blendFunc( gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA );
gl.enable( gl.BLEND );

gl.lineWidth( opts.projectileLineWidth );

webgl.data = [];

webgl.clear = function(){
	gl.clearColor( 0, 0, 0, 0 );
	gl.clear( gl.COLOR_BUFFER_BIT );
	webgl.data.length = 0;
}
webgl.draw = function( glType ){
	
	gl.bufferData( gl.ARRAY_BUFFER, new Float32Array( webgl.data ), gl.STATIC_DRAW );
	gl.drawArrays( glType, 0, webgl.data.length / 4 );
}

var	fireworks = []
	,	tick = 0
	,	sins = []
	,	coss = []
	,	maxShardsParFirework = opts.baseShardsParFirework + opts.addedShardsParFirework
	,	tau = 6.283185307179586476925286766559;

for( var i = 0; i < maxShardsParFirework; ++i ){
	sins[ i ] = Math.sin( tau * i / maxShardsParFirework );
	coss[ i ] = Math.cos( tau * i / maxShardsParFirework );
}

function Firework(){
	this.reset();
	this.shards = [];
	for( var i = 0; i < maxShardsParFirework; ++i )
		this.shards.push( new Shard( this ) );
}
Firework.prototype.reset = function(){
	
	var angle = -Math.PI / 2 + ( Math.random() - .5 )* opts.fireworkAngleSpan
		,	vel = opts.baseFireworkVel + opts.addedFireworkVel * Math.random();
	
	this.mode = 0;
	this.vx = vel * Math.cos( angle );
	this.vy = vel * Math.sin( angle );
	
	this.x = Math.random() * w;
	this.y = h;
	
	this.hue = tick * opts.initHueMultiplier;
	
}
Firework.prototype.step = function(){
	
	if( this.mode === 0 ){
		
		var ph = this.hue
			,	px = this.x
			,	py = this.y;
		
		this.hue += opts.runHueAdder;
	
		this.x += this.vx *= opts.xFriction;
		this.y += this.vy += opts.gravity;
		
		webgl.data.push(
			px, py, ph, opts.projectileAlpha * .8,
			this.x, this.y, this.hue, opts.projectileAlpha * .8 );
		
		if( this.vy >= opts.lowVelBoundary ){
			this.mode = 1;

			this.shardAmount = opts.baseShardsParFirework + opts.addedShardsParFirework * Math.random() | 0;

			var baseAngle = Math.random() * tau
				,	x = Math.cos( baseAngle )
				,	y = Math.sin( baseAngle )
				,	sin = sins[ this.shardAmount ]
				,	cos = coss[ this.shardAmount ];

			for( var i = 0; i < this.shardAmount; ++i ){

				var vel = opts.baseShardVel + opts.addedShardVel * Math.random();
				this.shards[ i ].reset( x * vel, y * vel )
				var X = x;
				x = x * cos - y * sin;
				y = y * cos + X * sin;
			}
		}

	} else if( this.mode === 1 ) {
		
		this.ph = this.hue
		this.hue += opts.runHueAdder;
		
		var allDead = true;
		for( var i = 0; i < this.shardAmount; ++i ){
			var shard = this.shards[ i ];
			if( !shard.dead ){
				shard.step();
				allDead = false;
			}
		}
		
		if( allDead )
			this.reset();
	}
	
}
function Shard( parent ){
	this.parent = parent;
}
Shard.prototype.reset = function( vx, vy ){
	this.x = this.parent.x;
	this.y = this.parent.y;
	this.vx = this.parent.vx * opts.shardFireworkVelMultiplier + vx;
	this.vy = this.parent.vy * opts.shardFireworkVelMultiplier + vy;
	this.dead = false;
	this.life = 0;
	this.ttl = opts.shardTTL;
	this.trail = [ this.x, this.y ];
}
Shard.prototype.step = function(){
	this.x += this.vx *= opts.xFriction;
	this.y += this.vy += opts.gravity;
	
	this.trail.push( this.x, this.y );
	var maxTrail = opts.shardTrailLength * 2;
	if( this.trail.length > maxTrail )
		this.trail.splice( 0, this.trail.length - maxTrail );
	
	var segments = this.trail.length / 2 - 1;
	if( segments > 0 ){
		for( var i = 2, s = 0; i < this.trail.length; i += 2, ++s ){
			var fade = ( s + 1 ) / segments;
			var a = opts.projectileAlpha * fade;
			webgl.data.push(
				this.trail[ i - 2 ], this.trail[ i - 1 ], this.parent.ph, a,
				this.trail[ i ], this.trail[ i + 1 ], this.parent.hue, a );
		}
	}
	
	this.life++;
	if( this.life >= this.ttl || this.y > h )
		this.dead = true;
}

function anim(){
	
	window.requestAnimationFrame( anim )
	
	webgl.clear();
	
	++tick;
	
	if( fireworks.length < opts.fireworks )
		fireworks.push( new Firework );
	
	fireworks.map( function( firework ){ firework.step(); } );
	
	webgl.draw( gl.LINES );
}
anim();

window.addEventListener( 'resize', function(){
	
	w = c.width = window.innerWidth;
	h = c.height = window.innerHeight;
	
	gl.viewport( 0, 0, w, h );
	gl.uniform2f( webgl.resUniformLoc, w, h );
})
window.addEventListener( 'click', function( e ){
	var firework = new Firework();
	firework.x = e.clientX;
	firework.y = e.clientY;
	firework.vx = 0;
	firework.vy = 0;
	fireworks.push( firework );
});