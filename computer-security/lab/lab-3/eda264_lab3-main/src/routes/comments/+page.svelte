<script lang="ts">
	import Navbar from '../navbar.svelte';
	import Footer from '../footer.svelte';
	/** @type {import('./$types').PageData} */
	export let data;
</script>

<main>
	<div class="flex flex-col h-screen">
		<Navbar sessionid={data.sessionid} />
		<div class="flex-grow flex grid max-md:grid-rows-2 md:grid-cols-2 m-2 my-4 ml-10">
			<tbody class="flex-auto">
				{#each data.comments as comment}
					<tr class="mx-3 gap-3 odd:bg-white even:bg-slate-100">
						<td>"{@html comment.Html}"</td>
						<td>by {comment.Username} at {comment.Timestamp}</td>
					</tr>
				{/each}
			</tbody>

			<div class="mx-auto max-md:row-start-1">
				<form method="POST" action="?/comment">
					<textarea
						name="message"
						rows="3"
						class="block p-3 w-full text-base text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-purple-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500"
						placeholder="Comment"
					></textarea>
					<button
						class="shadow bg-purple-500 hover:bg-purple-400 focus:shadow-outline focus:outline-none text-white font-bold py-2 px-4 rounded my-2"
						>upload</button
					>
				</form>

				<div class="mx-auto text-slate-500">
					<p>Hint: you can use the html image tag to display images here</p>
					<p>Just upload the file on <a href="/upload" class="text-purple-500">upload</a></p>
				</div>
			</div>
		</div>
		<Footer />
	</div>
</main>
