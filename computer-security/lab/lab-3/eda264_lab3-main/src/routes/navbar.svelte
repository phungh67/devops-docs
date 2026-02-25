<script lang="ts">
	/** @type {import('./$types').PageData} */
	export let sessionid: string;

	/** @type {import('./$types').ActionData} */
	const navItems = [
		{ label: 'upload', href: '/upload' },
		{ label: 'comments', href: '/comments' }
	];
</script>

<nav>
	<div class="px-2 sm:px-6 lg:px-8 bg-gray-400">
		<div
			class="mx-auto h-500 max-w-7xl py-4 justify-self-center flex justify-between align-baseline"
		>
			<a class="place-self-start my-auto left-0 flex-none font-permanent text-2xl" href="/">
				Sonic Death Monkey
			</a>
			{#if sessionid}
				<div class="relative flex justify-content-between">
					<ul class="justify-self-start flex-auto">
						<div class="flex gap-3">
							{#each navItems as item}
								<a href={item.href} class="text-sky-50 font-semibold py-2 px-4">{item.label}</a>
							{/each}
						</div>
					</ul>
					<ul class="mx-auto right-0 flex-initial">
						<form
							method="POST"
							action="/?/logout"
							class="bg-transparent hover:bg-sky-50 text-sky-50 font-semibold hover:text-black py-2 px-4 border border-sky-50 hover:border-transparent rounded"
						>
							<button>logout</button>
						</form>
					</ul>
				</div>
			{:else}
				<ul class="relative flex justify-content-end right-0">
					<form method="POST" action="/?/login">
						<label>
							<input
								name="username"
								type="username"
								placeholder="Username"
								class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							/>
						</label>
						<label>
							<input
								name="password"
								type="password"
								placeholder="Password"
								class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							/>
						</label>
						<button
							class="bg-transparent hover:bg-sky-50 text-sky-50 font-semibold hover:text-black py-2 px-4 border border-sky-50 hover:border-transparent rounded"
							>login</button
						>
					</form>
				</ul>
			{/if}
		</div>
	</div>
</nav>
