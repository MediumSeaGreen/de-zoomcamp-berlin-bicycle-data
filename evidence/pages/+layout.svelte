<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	export let data;
</script>

<EvidenceDefaultLayout {data} hideSidebar=true title='Fahrradbarometer Berlin' neverShowQueries=true githubRepo='https://github.com/MediumSeaGreen/de-zoomcamp-berlin-bicycle-data'>
	<slot slot="content" />
</EvidenceDefaultLayout>
