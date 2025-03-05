import type { CustomThemeConfig } from '@skeletonlabs/tw-plugin';

export const localAIBenchTheme: CustomThemeConfig = {
	name: 'local-ai-bench-theme',
	properties: {
		// =~= Theme Properties =~=
		"--theme-font-family-base": `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace`,
		"--theme-font-family-heading": `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace`,
		"--theme-font-color-base": "var(--color-success-900)",
		"--theme-font-color-dark": "var(--color-success-600)",
		"--theme-rounded-base": "9999px",
		"--theme-rounded-container": "12px",
		"--theme-border-base": "1px",
		// =~= Theme On-X Colors =~=
		"--on-primary": "255 255 255",
		"--on-secondary": "255 255 255",
		"--on-tertiary": "var(--color-success-900)",
		"--on-success": "0 0 0",
		"--on-warning": "0 0 0",
		"--on-error": "255 255 255",
		"--on-surface": "255 255 255",
		// =~= Theme Colors  =~=
		// primary | #5A24A6 
		"--color-primary-50": "230 222 242", // #e6def2
		"--color-primary-100": "222 211 237", // #ded3ed
		"--color-primary-200": "214 200 233", // #d6c8e9
		"--color-primary-300": "189 167 219", // #bda7db
		"--color-primary-400": "140 102 193", // #8c66c1
		"--color-primary-500": "90 36 166", // #5A24A6
		"--color-primary-600": "81 32 149", // #512095
		"--color-primary-700": "68 27 125", // #441b7d
		"--color-primary-800": "54 22 100", // #361664
		"--color-primary-900": "44 18 81", // #2c1251
		// secondary | #9f96d9 
		"--color-secondary-50": "241 239 249", // #f1eff9
		"--color-secondary-100": "236 234 247", // #eceaf7
		"--color-secondary-200": "231 229 246", // #e7e5f6
		"--color-secondary-300": "217 213 240", // #d9d5f0
		"--color-secondary-400": "188 182 228", // #bcb6e4
		"--color-secondary-500": "159 150 217", // #9f96d9
		"--color-secondary-600": "143 135 195", // #8f87c3
		"--color-secondary-700": "119 113 163", // #7771a3
		"--color-secondary-800": "95 90 130", // #5f5a82
		"--color-secondary-900": "78 74 106", // #4e4a6a
		// tertiary | #cbc5d9 
		"--color-tertiary-50": "247 246 249", // #f7f6f9
		"--color-tertiary-100": "245 243 247", // #f5f3f7
		"--color-tertiary-200": "242 241 246", // #f2f1f6
		"--color-tertiary-300": "234 232 240", // #eae8f0
		"--color-tertiary-400": "219 214 228", // #dbd6e4
		"--color-tertiary-500": "203 197 217", // #cbc5d9
		"--color-tertiary-600": "183 177 195", // #b7b1c3
		"--color-tertiary-700": "152 148 163", // #9894a3
		"--color-tertiary-800": "122 118 130", // #7a7682
		"--color-tertiary-900": "99 97 106", // #63616a
		// success | #bddaaa 
		"--color-success-50": "245 249 242", // #f5f9f2
		"--color-success-100": "242 248 238", // #f2f8ee
		"--color-success-200": "239 246 234", // #eff6ea
		"--color-success-300": "229 240 221", // #e5f0dd
		"--color-success-400": "209 229 196", // #d1e5c4
		"--color-success-500": "189 218 170", // #bddaaa
		"--color-success-600": "170 196 153", // #aac499
		"--color-success-700": "142 164 128", // #8ea480
		"--color-success-800": "113 131 102", // #718366
		"--color-success-900": "93 107 83", // #5d6b53
		// warning | #EAB308 
		"--color-warning-50": "252 244 218", // #fcf4da
		"--color-warning-100": "251 240 206", // #fbf0ce
		"--color-warning-200": "250 236 193", // #faecc1
		"--color-warning-300": "247 225 156", // #f7e19c
		"--color-warning-400": "240 202 82", // #f0ca52
		"--color-warning-500": "234 179 8", // #EAB308
		"--color-warning-600": "211 161 7", // #d3a107
		"--color-warning-700": "176 134 6", // #b08606
		"--color-warning-800": "140 107 5", // #8c6b05
		"--color-warning-900": "115 88 4", // #735804
		// error | #a62424 
		"--color-error-50": "242 222 222", // #f2dede
		"--color-error-100": "237 211 211", // #edd3d3
		"--color-error-200": "233 200 200", // #e9c8c8
		"--color-error-300": "219 167 167", // #dba7a7
		"--color-error-400": "193 102 102", // #c16666
		"--color-error-500": "166 36 36", // #a62424
		"--color-error-600": "149 32 32", // #952020
		"--color-error-700": "125 27 27", // #7d1b1b
		"--color-error-800": "100 22 22", // #641616
		"--color-error-900": "81 18 18", // #511212
		// surface | #2b3040 
		"--color-surface-50": "223 224 226", // #dfe0e2
		"--color-surface-100": "213 214 217", // #d5d6d9
		"--color-surface-200": "202 203 207", // #cacbcf
		"--color-surface-300": "170 172 179", // #aaacb3
		"--color-surface-400": "107 110 121", // #6b6e79
		"--color-surface-500": "43 48 64", // #2b3040
		"--color-surface-600": "39 43 58", // #272b3a
		"--color-surface-700": "32 36 48", // #202430
		"--color-surface-800": "26 29 38", // #1a1d26
		"--color-surface-900": "21 24 31", // #15181f
	}
};