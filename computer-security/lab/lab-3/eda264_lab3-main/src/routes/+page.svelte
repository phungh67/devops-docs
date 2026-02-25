<script lang="ts">
	import Navbar from './navbar.svelte';
	import Footer from './footer.svelte';
	/** @type {import('./$types').PageData} */
	export let data;

	/** @type {import('./$types').ActionData} */
	export let form;
</script>

<main>
	<div class="flex flex-col h-screen">
		<Navbar sessionid={data.sessionid} />

		{#if form?.success}
			<p class="mx-auto h-500 max-w-7xl py-4 text-lg">
				Successfully logged in! Welcome back, {data.user.Username}
			</p>
		{/if}

		<p class="flex-grow mx-auto h-500 max-w-7xl py-4 justify-self-center flex justify-between">
			Everything Sonic Death Monkey. Enter the site. Members only ...
			<br />
			Go figure it out for yourself. I double-dare you!
			<br />
			<br />
			Page lacks content? YOU lack content.
		</p>

		<Footer />
	</div>
</main>
