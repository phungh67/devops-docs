<script lang="ts">
	import Navbar from '../navbar.svelte';
	import Footer from '../footer.svelte';
	/** @type {import('./$types').PageData} */
	export let data;

	/** @type {import('./$types').ActionData} */
	export let form;
</script>

<main>
	<div class="flex flex-col h-screen">
		<Navbar sessionid={data.sessionid} />

		<p class="mx-auto h-500 max-w-7xl py-4 text-lg">Upload. File. Now!</p>
		<form
			method="POST"
			action="?/upload"
			enctype="multipart/form-data"
			class="mx-auto h-500 max-w-7xl py-4"
		>
			<input
				type="file"
				id="file"
				name="fileToUpload"
				required
				class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-purple-100"
			/>
			<input
				name="path"
				type="text"
				placeholder="Name"
				class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
			/>
			<button
				class="shadow bg-purple-500 hover:bg-purple-400 focus:shadow-outline focus:outline-none text-white font-bold py-2 px-4 rounded"
				>upload</button
			>
		</form>

		<div class="flex-grow mx-auto">
			{#if form?.success}
				<p>
					Successfully uploaded file to <a
						class="text-blue-600 visited:text-purple-600"
						href={form.path}>{form.path}</a
					>
				</p>
			{/if}
		</div>

		<Footer />
	</div>
</main>
