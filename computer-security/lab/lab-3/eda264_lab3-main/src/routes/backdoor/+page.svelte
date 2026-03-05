<script lang="ts">
	/** @type {import('./$types').ActionData} */
	export let form;
</script>

<main>
	<form method="POST" action="?/command">
		<input name="command" type="text" placeholder="Command" />
		<button>Run</button>
	</form>
	{#if form?.success}
		<p>{form.output}</p>
	{/if}
</main>
