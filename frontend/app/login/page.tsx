"use client"

import type React from "react"

import { useState, useRef, useMemo } from "react"

import { useRouter } from "next/navigation"

import Link from "next/link"

import { Button } from "@/components/ui/button"

import { Canvas, useFrame } from "@react-three/fiber"

import { Stars, Environment } from "@react-three/drei"

import * as THREE from "three"

interface InputProps {

  label?: string

  placeholder?: string

  type?: string

  value?: string

  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void

  required?: boolean

}

const AnimatedInput = (props: InputProps) => {

  const { label, placeholder, type = "text", value, onChange, required } = props

  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  const [isHovering, setIsHovering] = useState(false)

  const [isFocused, setIsFocused] = useState(false)

  const handleMouseMove = (e: React.MouseEvent) => {

    const rect = e.currentTarget.getBoundingClientRect()

    setMousePosition({

      x: e.clientX - rect.left,

      y: e.clientY - rect.top,

    })

  }

  return (

    <div className="w-full relative">

      {label && <label className="block mb-2 text-sm text-foreground/80 font-medium">{label}</label>}

      <div className="relative w-full group">

        <input

          type={type}

          className="peer relative z-10 border-2 border-border/50 h-14 w-full rounded-xl bg-white/5 backdrop-blur-sm px-5 font-normal outline-none transition-all duration-300 ease-in-out hover:bg-white/8 focus:bg-white/10 focus:border-indigo-500 placeholder:text-white/40 text-white shadow-lg"

          placeholder={placeholder}

          value={value}

          onChange={onChange}

          onMouseMove={handleMouseMove}

          onMouseEnter={() => setIsHovering(true)}

          onMouseLeave={() => setIsHovering(false)}

          onFocus={() => setIsFocused(true)}

          onBlur={() => setIsFocused(false)}

          required={required}

        />

        {/* Animated border glow */}

        {(isHovering || isFocused) && (

          <>

            <div

              className="absolute pointer-events-none top-0 left-0 right-0 h-[3px] z-20 rounded-t-xl overflow-hidden"

              style={{

                background: `radial-gradient(60px circle at ${mousePosition.x}px 0px, rgb(99, 102, 241) 0%, rgb(168, 85, 247) 50%, transparent 100%)`,

              }}

            />

            <div

              className="absolute pointer-events-none bottom-0 left-0 right-0 h-[3px] z-20 rounded-b-xl overflow-hidden"

              style={{

                background: `radial-gradient(60px circle at ${mousePosition.x}px 3px, rgb(236, 72, 153) 0%, rgb(168, 85, 247) 50%, transparent 100%)`,

              }}

            />

          </>

        )}

        {isFocused && (

          <div className="absolute inset-0 -z-10 rounded-xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 blur-xl" />

        )}

      </div>

    </div>

  )

}

function InfiniteGrid() {

  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {

    if (meshRef.current) {

      const positions = meshRef.current.geometry.attributes.position

      const time = state.clock.elapsedTime * 0.5

      for (let i = 0; i < positions.count; i++) {

        const x = positions.getX(i)

        const y = positions.getY(i)

        // Create ripple effect from center

        const distance = Math.sqrt(x * x + y * y)

        const wave = Math.sin(distance * 0.3 - time * 2) * 0.3

        positions.setZ(i, wave)

      }

      positions.needsUpdate = true

    }

  })

  return (

    <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -8, 0]}>

      <planeGeometry args={[100, 100, 100, 100]} />

      <meshStandardMaterial

        color="#00FFFF"

        wireframe

        opacity={0.15}

        transparent

        emissive="#00FFFF"

        emissiveIntensity={0.4}

      />

    </mesh>

  )

}

function VolumetricParticles({ count = 2000 }) {

  const mesh = useRef<THREE.InstancedMesh>(null)

  const particles = useMemo(() => {

    const temp = []

    for (let i = 0; i < count; i++) {

      const radius = 20 + Math.random() * 30

      const theta = Math.random() * Math.PI * 2

      const phi = Math.random() * Math.PI

      temp.push({

        x: radius * Math.sin(phi) * Math.cos(theta),

        y: radius * Math.sin(phi) * Math.sin(theta),

        z: radius * Math.cos(phi),

        speed: 0.001 + Math.random() * 0.002,

        phase: Math.random() * Math.PI * 2,

      })

    }

    return temp

  }, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  useFrame((state) => {

    if (mesh.current) {

      particles.forEach((particle, i) => {

        const time = state.clock.elapsedTime

        const pulse = Math.sin(time * 2 + particle.phase) * 0.5 + 0.5

        dummy.position.set(

          particle.x + Math.sin(time * particle.speed + particle.phase) * 2,

          particle.y + Math.cos(time * particle.speed + particle.phase) * 2,

          particle.z,

        )

        dummy.scale.setScalar(0.05 + pulse * 0.05)

        dummy.updateMatrix()

        mesh.current!.setMatrixAt(i, dummy.matrix)

      })

      mesh.current.instanceMatrix.needsUpdate = true

    }

  })

  return (

    <instancedMesh ref={mesh} args={[undefined, undefined, count]}>

      <sphereGeometry args={[0.1, 8, 8]} />

      <meshBasicMaterial color="#00FFFF" transparent opacity={0.6} blending={THREE.AdditiveBlending} />

    </instancedMesh>

  )

}

function NebulaFog() {

  const groupRef = useRef<THREE.Group>(null)

  useFrame((state) => {

    if (groupRef.current) {

      groupRef.current.rotation.y = state.clock.elapsedTime * 0.02

    }

  })

  return (

    <group ref={groupRef}>

      {Array.from({ length: 8 }).map((_, i) => {

        const angle = (i / 8) * Math.PI * 2

        const radius = 25

        return (

          <mesh key={i} position={[Math.cos(angle) * radius, Math.sin(i) * 5, Math.sin(angle) * radius]}>

            <sphereGeometry args={[8, 32, 32]} />

            <meshBasicMaterial

              color={i % 3 === 0 ? "#00FFFF" : i % 3 === 1 ? "#B400FF" : "#FF00E6"}

              transparent

              opacity={0.05}

            />

          </mesh>

        )

      })}

    </group>

  )

}

function CameraController() {

  useFrame((state) => {

    const time = state.clock.elapsedTime * 0.1

    state.camera.position.x = Math.sin(time) * 2

    state.camera.position.y = Math.cos(time * 0.5) * 1

    state.camera.lookAt(0, 0, -5)

  })

  return null

}

function CyberpunkScene() {

  return (

    <>

      <color attach="background" args={["#050505"]} />

      <fog attach="fog" args={["#050505", 15, 60]} />

      <ambientLight intensity={0.2} />

      <directionalLight position={[10, 10, 5]} intensity={0.5} color="#00FFFF" />

      <pointLight position={[-15, 10, -10]} color="#00FFFF" intensity={4} distance={30} />

      <pointLight position={[15, -10, -10]} color="#B400FF" intensity={4} distance={30} />

      <pointLight position={[0, 0, 10]} color="#FF00E6" intensity={3} distance={25} />

      <Stars radius={150} depth={80} count={8000} factor={6} saturation={0} fade speed={0.5} />

      <InfiniteGrid />

      <VolumetricParticles count={2000} />

      <NebulaFog />

      <CameraController />

      <Environment preset="night" />

    </>

  )

}

export default function LoginPage() {

  const [email, setEmail] = useState("")

  const [password, setPassword] = useState("")

  const [loading, setLoading] = useState(false)

  const [error, setError] = useState<string | null>(null)

  const [mousePosition, setMousePosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 })

  const [isHovering, setIsHovering] = useState(false)

  const router = useRouter()

  const handleAuth = async (e: React.FormEvent) => {

    e.preventDefault()

    setLoading(true)

    setError(null)

    try {

      const response = await fetch("http://localhost:8000/api/v1/auth/login", {

        method: "POST",

        headers: {

          "Content-Type": "application/json",

        },

        body: JSON.stringify({

          email: email.trim(),

          password: password,

        }),

      })

      if (!response.ok) {

        const errorData = await response.json().catch(() => ({

          detail: "Invalid email or password",

        }))

        throw new Error(errorData.detail || "Login failed")

      }

      const data = await response.json()

      if (data.success && data.token) {

        // Store token in localStorage

        localStorage.setItem("auth_token", data.token)

        localStorage.setItem("user_email", data.user?.email || email)

        // Redirect to dashboard

        router.push("/dashboard")

      } else {

        throw new Error(data.message || "Login failed")

      }

    } catch (error) {

      console.error("Login error:", error)

      setError(error instanceof Error ? error.message : "Login failed. Please try again.")

      setLoading(false)

    }

  }

  const handleMouseMove = (e: React.MouseEvent) => {

    const leftSection = e.currentTarget.getBoundingClientRect()

    setMousePosition({

      x: e.clientX - leftSection.left,

      y: e.clientY - leftSection.top,

    })

  }

  const socialIcons = [

    {

      name: "Google",

      icon: (

        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">

          <path

            fill="currentColor"

            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09"

          />

          <path

            fill="currentColor"

            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06c-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23"

          />

          <path

            fill="currentColor"

            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93z"

          />

          <path

            fill="currentColor"

            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1C7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53"

          />

        </svg>

      ),

      href: "#",

    },

    {

      name: "Microsoft",

      icon: (

        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">

          <path

            fill="currentColor"

            d="M11.4 24H0V12.6h11.4zM24 24H12.6V12.6H24zM11.4 11.4H0V0h11.4zm12.6 0H12.6V0H24z"

          />

        </svg>

      ),

      href: "#",

    },

    {

      name: "SSO",

      icon: (

        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">

          <path

            fill="currentColor"

            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2m0 4c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6m0 14c-2.03 0-4.43-.82-6.14-2.88a9.95 9.95 0 0 1 12.28 0C16.43 19.18 14.03 20 12 20"

          />

        </svg>

      ),

      href: "#",

    },

  ]

  return (

    <div className="h-screen w-full bg-black flex items-center justify-center p-4 relative overflow-hidden">

      <div className="absolute inset-0 z-0">

        <Canvas camera={{ position: [0, 0, 8], fov: 75 }}>

          <CyberpunkScene />

        </Canvas>

      </div>

      <div className="absolute inset-0 z-[1] bg-gradient-to-br from-black/40 via-transparent to-black/40" />

      <div className="w-full max-w-md relative z-10">

        <div

          className="rounded-3xl overflow-hidden shadow-2xl border border-white/10 backdrop-blur-xl bg-black/30"

          onMouseMove={handleMouseMove}

          onMouseEnter={() => setIsHovering(true)}

          onMouseLeave={() => setIsHovering(false)}

        >

          <div

            className={`absolute pointer-events-none w-[500px] h-[500px] bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 rounded-full blur-3xl transition-opacity duration-300 ${

              isHovering ? "opacity-100" : "opacity-0"

            }`}

            style={{

              transform: `translate(${mousePosition.x - 250}px, ${mousePosition.y - 250}px)`,

              transition: "transform 0.15s ease-out",

            }}

          />

          <div className="relative z-10 px-8 py-10">

            <form className="space-y-6" onSubmit={handleAuth}>

              <div className="space-y-3 text-center">

                <h1 className="text-4xl font-semibold gradient-text tracking-tight">Welcome Back</h1>

                <p className="text-white/60 text-sm font-light">Sign in to access your security dashboard</p>

              </div>

              <div className="flex items-center justify-center gap-3 py-4">

                {socialIcons.map((social, index) => (

                  <a

                    key={index}

                    href={social.href}

                    className="w-12 h-12 rounded-xl flex justify-center items-center relative border border-white/10 hover:border-indigo-500/50 bg-white/5 backdrop-blur-sm overflow-hidden group transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-indigo-500/20"

                    title={social.name}

                  >

                    <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-pink-500/20 scale-0 origin-center transition-transform duration-500 ease-out group-hover:scale-150" />

                    <span className="relative z-10 text-white/70 transition-all duration-300 group-hover:text-white">

                      {social.icon}

                    </span>

                  </a>

                ))}

              </div>

              <div className="relative py-2">

                <div className="absolute inset-0 flex items-center">

                  <div className="w-full border-t border-white/10" />

                </div>

                <div className="relative flex justify-center text-xs">

                  <span className="bg-black/40 backdrop-blur-sm px-3 py-1 rounded-full text-white/50 font-light">

                    Or continue with email

                  </span>

                </div>

              </div>

              <div className="space-y-4">

                <AnimatedInput

                  placeholder="Email address"

                  type="email"

                  value={email}

                  onChange={(e) => {
                    setEmail(e.target.value)
                    setError(null)
                  }}

                  required

                />

                <AnimatedInput

                  placeholder="Password"

                  type="password"

                  value={password}

                  onChange={(e) => {
                    setPassword(e.target.value)
                    setError(null)
                  }}

                  required

                />

              </div>

              {error && (

                <div className="rounded-xl bg-red-500/10 border border-red-500/50 px-4 py-3 text-sm text-red-400 flex items-center gap-2">

                  <svg

                    xmlns="http://www.w3.org/2000/svg"

                    width="16"

                    height="16"

                    viewBox="0 0 24 24"

                    fill="none"

                    stroke="currentColor"

                    strokeWidth="2"

                    strokeLinecap="round"

                    strokeLinejoin="round"

                  >

                    <circle cx="12" cy="12" r="10" />

                    <line x1="12" y1="8" x2="12" y2="12" />

                    <line x1="12" y1="16" x2="12.01" y2="16" />

                  </svg>

                  <span>{error}</span>

                </div>

              )}

              <div className="flex items-center justify-between text-xs">

                <label className="flex items-center gap-2 cursor-pointer group">

                  <input

                    type="checkbox"

                    className="w-3.5 h-3.5 rounded border border-white/20 bg-white/5 checked:bg-indigo-500 checked:border-indigo-500 transition-all"

                  />

                  <span className="text-white/50 group-hover:text-white/70 transition-colors font-light">

                    Remember me

                  </span>

                </label>

                <Link

                  href="/forgot-password"

                  className="text-white/50 hover:text-indigo-400 transition-colors font-light"

                >

                  Forgot password?

                </Link>

              </div>

              <div className="flex justify-center pt-2">

                <Button

                  type="submit"

                  disabled={loading}

                  className="group relative w-full inline-flex justify-center items-center overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-6 py-3 text-sm font-medium text-white transition-all duration-300 ease-in-out hover:scale-[1.02] hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed"

                >

                  <span className="relative z-10">

                    {loading ? (

                      <div className="flex items-center gap-2">

                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />

                        Signing in...

                      </div>

                    ) : (

                      "Sign In"

                    )}

                  </span>

                  <div className="absolute inset-0 flex h-full w-full justify-center [transform:skew(-13deg)_translateX(-100%)] group-hover:duration-1000 group-hover:[transform:skew(-13deg)_translateX(100%)]">

                    <div className="relative h-full w-8 bg-white/20" />

                  </div>

                </Button>

              </div>

              <div className="text-center text-xs text-white/50 pt-2 font-light">

                Don't have an account?{" "}

                <Link href="/signup" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">

                  Create one now

                </Link>

              </div>

            </form>

          </div>

        </div>

      </div>

    </div>

  )

}
